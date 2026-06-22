# experiment/metrics.py -- Review report comparison metrics.
#
# Measures: claim-level fuzzy overlap, word Jaccard, section completeness,
#           section length ratio, token efficiency, and semantic similarity
#           (char n-gram TF-IDF cosine at section level).

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from deepreview.report.final_report import (
    _REQUIRED_SECTION_GROUPS,
    find_missing_required_sections,
)

# ---- Constants -------------------------------------------------------------

_MIN_CLAIM_LENGTH = 15
_SIMILARITY_THRESHOLD = 0.25
_TOP_WORDS = 200

_STOPWORDS: set[str] = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "shall", "this", "that",
    "these", "those", "it", "its", "we", "they", "he", "she", "his",
    "her", "their", "our", "not", "no", "as", "if", "so", "than",
    "also", "very", "just", "about", "into", "over", "after", "before",
    "between", "under", "each", "all", "some", "any", "both", "such",
    "only", "other", "more", "most", "new", "one", "two", "first",
}

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?\n])\s+")
_WORD_TOKEN = re.compile(r"[a-zA-Z]{3,}")
_HEADING_PATTERN = re.compile(r"^#{1,3}\s+(.+)$", re.MULTILINE)
_CODE_BLOCK = re.compile(r"```[\s\S]*?```")
_INLINE_CODE = re.compile(r"`[^`\n]+`")
_URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")


# ---- Data structures -------------------------------------------------------

@dataclass
class ExperimentMetrics:
    run_ids: list[str] = field(default_factory=list)
    claim_overlap_matrix: dict[str, dict[str, float]] = field(default_factory=dict)
    word_jaccard_matrix: dict[str, dict[str, float]] = field(default_factory=dict)
    semantic_similarity_matrix: dict[str, dict[str, float]] = field(default_factory=dict)
    section_completeness: dict[str, dict[str, int]] = field(default_factory=dict)
    section_counts: dict[str, int] = field(default_factory=dict)
    costs: dict[str, float] = field(default_factory=dict)
    token_usage: dict[str, dict[str, int]] = field(default_factory=dict)

    def strategy_self_consistency(self, strategy_prefix: str) -> float | None:
        runs = [rid for rid in self.run_ids if rid.startswith(strategy_prefix)]
        if len(runs) < 2:
            return None
        values = []
        for i in range(len(runs)):
            for j in range(i + 1, len(runs)):
                val = self.claim_overlap_matrix.get(runs[i], {}).get(runs[j])
                if val is not None:
                    values.append(val)
        return sum(values) / len(values) if values else None

    def strategy_semantic_consistency(self, strategy_prefix: str) -> float | None:
        """Self-consistency using char n-gram TF-IDF cosine similarity."""
        runs = [rid for rid in self.run_ids if rid.startswith(strategy_prefix)]
        if len(runs) < 2:
            return None
        values = []
        for i in range(len(runs)):
            for j in range(i + 1, len(runs)):
                val = self.semantic_similarity_matrix.get(runs[i], {}).get(runs[j])
                if val is not None:
                    values.append(val)
        return sum(values) / len(values) if values else None

    def strategy_avg_cost(self, strategy_prefix: str) -> float | None:
        runs = [rid for rid in self.run_ids if rid.startswith(strategy_prefix)]
        values = [self.costs.get(r, 0) for r in runs]
        return sum(values) / len(values) if values else None

    def strategy_avg_section_count(self, strategy_prefix: str) -> float | None:
        runs = [rid for rid in self.run_ids if rid.startswith(strategy_prefix)]
        values = [self.section_counts.get(r, 0) for r in runs]
        return sum(values) / len(values) if values else None


# ---- Text cleaning ---------------------------------------------------------

def _clean_text(text: str) -> str:
    t = str(text or "")
    t = _CODE_BLOCK.sub(" ", t)
    t = _INLINE_CODE.sub(" ", t)
    t = _URL_PATTERN.sub(" ", t)
    return t


# ---- Sentence / claim extraction -------------------------------------------

def _extract_claims(text: str) -> list[str]:
    cleaned = _clean_text(text)
    sentences = _SENTENCE_SPLIT.split(cleaned)
    claims = []
    for s in sentences:
        s = s.strip()
        if not s or s.startswith("|") or s.startswith("---"):
            continue
        if s.startswith("- ") or s.startswith("* "):
            s = s[2:].strip()
        if s.startswith("#"):
            continue
        if len(s) >= _MIN_CLAIM_LENGTH:
            claims.append(s)
    return claims


# ---- Section splitting -----------------------------------------------------

def _split_by_h2_sections(markdown: str) -> dict[str, str]:
    """Split markdown into top-level sections by ## headings only.
    ### sub-sections remain inside their parent ## section text.
    """
    lines = markdown.split("\n")
    sections: dict[str, list[str]] = {}
    current = "_preamble"
    sections[current] = []
    for line in lines:
        m = re.match(r"^##\s+(.+)", line)
        if m:
            current = m.group(1).strip()
            if current not in sections:
                sections[current] = []
            continue
        sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def _split_by_sections(markdown: str) -> dict[str, str]:
    sections = _split_by_h2_sections(markdown)
    result: dict[str, str] = {}
    for label, aliases in _REQUIRED_SECTION_GROUPS:
        for sec_name, body in sections.items():
            low = sec_name.lower()
            if any(a in low for a in aliases):
                if label not in result:
                    result[label] = body
                else:
                    result[label] += "\n" + body
    return result


# ---- Tokenisation ----------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _WORD_TOKEN.findall(_clean_text(text))
            if t.lower() not in _STOPWORDS]


# ---- Token Jaccard helper --------------------------------------------------

def _token_jaccard(tokens_a: list[str], tokens_b: list[str]) -> float:
    set_a = set(tokens_a)
    set_b = set(tokens_b)
    if not set_a and not set_b:
        return 0.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


# ---- Claim-level overlap (token Jaccard) -----------------------------------

def compute_claim_overlap(report_a: str, report_b: str) -> float:
    sections_a = _split_by_h2_sections(report_a)
    sections_b = _split_by_h2_sections(report_b)
    all_claims_a: list[str] = []
    all_claims_b: list[str] = []
    all_section_names = sorted(set(sections_a) | set(sections_b), key=lambda x: x.lower())
    paired_claims: list[tuple[list[str], list[str]]] = []
    for name in all_section_names:
        body_a = sections_a.get(name, "")
        body_b = sections_b.get(name, "")
        claims_a = _extract_claims(body_a)
        claims_b = _extract_claims(body_b)
        if claims_a or claims_b:
            paired_claims.append((claims_a, claims_b))
            all_claims_a.extend(claims_a)
            all_claims_b.extend(claims_b)
    if not all_claims_a and not all_claims_b:
        return 0.0
    total_matched = 0
    total_max = max(len(all_claims_a), len(all_claims_b))
    for ca, cb in paired_claims:
        if not ca or not cb:
            continue
        tokens_a = [_tokenize(c) for c in ca]
        tokens_b = [_tokenize(c) for c in cb]
        matched_b = set()
        for ta in tokens_a:
            for j, tb in enumerate(tokens_b):
                if j in matched_b:
                    continue
                if _token_jaccard(ta, tb) >= _SIMILARITY_THRESHOLD:
                    matched_b.add(j)
                    total_matched += 1
                    break
    return total_matched / total_max if total_max > 0 else 0.0


# ---- Semantic section similarity (char n-gram TF-IDF cosine) ----------------

def compute_semantic_section_similarity(report_a: str, report_b: str) -> float:
    """Section-level semantic similarity using char n-gram TF-IDF cosine.

    Splits both reports by ## sections, fits one TfidfVectorizer on the
    combined corpus of all section bodies, then computes cosine similarity
    per aligned section pair.  Returns a length-weighted average.

    Character n-grams (3-5) are language-agnostic and capture subword
    patterns robust to paraphrasing and mixed-language text.
    """
    sections_a = _split_by_h2_sections(report_a)
    sections_b = _split_by_h2_sections(report_b)

    all_names = sorted(set(sections_a) | set(sections_b), key=lambda x: x.lower())

    # Collect all section bodies + build per-name index
    corpus: list[str] = []
    idx_a: dict[str, int] = {}
    idx_b: dict[str, int] = {}
    for name in all_names:
        body_a = _clean_text(sections_a.get(name, ""))
        body_b = _clean_text(sections_b.get(name, ""))
        if body_a.strip():
            idx_a[name] = len(corpus)
            corpus.append(body_a)
        if body_b.strip():
            idx_b[name] = len(corpus)
            corpus.append(body_b)

    if len(corpus) < 2:
        return 0.0

    # Fit one vectorizer on all sections from both reports
    vec = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        max_features=3000,
        sublinear_tf=True,
    )
    try:
        tfidf = vec.fit_transform(corpus)
    except ValueError:
        return 0.0

    similarities: list[float] = []
    weights: list[float] = []

    for name in all_names:
        i_a = idx_a.get(name)
        i_b = idx_b.get(name)
        if i_a is None or i_b is None:
            continue
        sim = float(cosine_similarity(tfidf[i_a : i_a + 1], tfidf[i_b : i_b + 1])[0][0])
        weight = len(corpus[i_a]) + len(corpus[i_b])
        similarities.append(sim)
        weights.append(weight)

    if not similarities:
        return 0.0
    return float(np.average(similarities, weights=weights))


# ---- Global semantic similarity (simpler fallback) --------------------------

def compute_global_semantic_similarity(report_a: str, report_b: str) -> float:
    """Whole-report semantic similarity (single TF-IDF cosine).

    Vectorizes each report as a single document and computes cosine
    similarity.  Captures overall topical alignment.
    """
    a_clean = _clean_text(report_a)
    b_clean = _clean_text(report_b)
    vec = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        max_features=5000,
        sublinear_tf=True,
    )
    try:
        tfidf = vec.fit_transform([a_clean, b_clean])
        return float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
    except ValueError:
        return 0.0


# ---- Word Jaccard ----------------------------------------------------------

def compute_word_jaccard(report_a: str, report_b: str) -> float:
    tokens_a = _tokenize(report_a)
    tokens_b = _tokenize(report_b)
    freq_a = Counter(tokens_a).most_common(_TOP_WORDS)
    freq_b = Counter(tokens_b).most_common(_TOP_WORDS)
    words_a = {w for w, _ in freq_a}
    words_b = {w for w, _ in freq_b}
    if not words_a and not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


# ---- Section completeness --------------------------------------------------

def compute_section_completeness(report: str) -> dict[str, int]:
    """Return per-section word count for the 11 required sections.
    Uses _split_by_h2_sections so ### sub-headings count under their ## parent.
    """
    sections = _split_by_h2_sections(report)
    result: dict[str, int] = {}
    for label, aliases in _REQUIRED_SECTION_GROUPS:
        best_name = None
        best_len = 0
        for sec_name, body in sections.items():
            low = sec_name.lower()
            if any(a in low for a in aliases):
                wc = len(_tokenize(body))
                if wc > best_len:
                    best_len = wc
                    best_name = label
        result[label] = best_len
    result["_non_empty_count"] = sum(1 for v in result.values() if v > 0)
    return result


# ---- Section length ratio --------------------------------------------------

def compute_section_length_ratio(report_a: str, report_b: str) -> float:
    comp_a = compute_section_completeness(report_a)
    comp_b = compute_section_completeness(report_b)
    ratios = []
    for label, _ in _REQUIRED_SECTION_GROUPS:
        wa = comp_a.get(label, 0)
        wb = comp_b.get(label, 0)
        if wa == 0 and wb == 0:
            ratios.append(1.0)
        elif wa == 0 or wb == 0:
            ratios.append(0.0)
        else:
            ratios.append(min(wa, wb) / max(wa, wb))
    return sum(ratios) / len(ratios) if ratios else 0.0


# ---- Aggregate all metrics -------------------------------------------------

def compute_all_metrics(
    reports: dict[str, str],
    costs: dict[str, float] | None = None,
    token_usage: dict[str, dict[str, int]] | None = None,
) -> ExperimentMetrics:
    costs = costs or {}
    token_usage = token_usage or {}
    run_ids = sorted(reports.keys())
    n = len(run_ids)
    claim_mat: dict[str, dict[str, float]] = {}
    jaccard_mat: dict[str, dict[str, float]] = {}
    semantic_mat: dict[str, dict[str, float]] = {}
    section_comp: dict[str, dict[str, int]] = {}
    section_cnt: dict[str, int] = {}
    for rid in run_ids:
        report = reports.get(rid, "")
        section_comp[rid] = compute_section_completeness(report)
        section_cnt[rid] = section_comp[rid].get("_non_empty_count", 0)
    for i in range(n):
        claim_mat[run_ids[i]] = {}
        jaccard_mat[run_ids[i]] = {}
        semantic_mat[run_ids[i]] = {}
        for j in range(n):
            if i == j:
                claim_mat[run_ids[i]][run_ids[j]] = 1.0
                jaccard_mat[run_ids[i]][run_ids[j]] = 1.0
                semantic_mat[run_ids[i]][run_ids[j]] = 1.0
            elif j < i:
                claim_mat[run_ids[i]][run_ids[j]] = claim_mat[run_ids[j]][run_ids[i]]
                jaccard_mat[run_ids[i]][run_ids[j]] = jaccard_mat[run_ids[j]][run_ids[i]]
                semantic_mat[run_ids[i]][run_ids[j]] = semantic_mat[run_ids[j]][run_ids[i]]
            else:
                claim_mat[run_ids[i]][run_ids[j]] = compute_claim_overlap(
                    reports[run_ids[i]], reports[run_ids[j]]
                )
                jaccard_mat[run_ids[i]][run_ids[j]] = compute_word_jaccard(
                    reports[run_ids[i]], reports[run_ids[j]]
                )
                semantic_mat[run_ids[i]][run_ids[j]] = compute_semantic_section_similarity(
                    reports[run_ids[i]], reports[run_ids[j]]
                )
    return ExperimentMetrics(
        run_ids=run_ids,
        claim_overlap_matrix=claim_mat,
        word_jaccard_matrix=jaccard_mat,
        semantic_similarity_matrix=semantic_mat,
        section_completeness=section_comp,
        section_counts=section_cnt,
        costs=dict(costs),
        token_usage=dict(token_usage),
    )