# iterative_agent_prompt.py -- Round-specific prompts for iterative multi-round review.
#
# Strategy:
#   R1 (DISCOVER):  exhaustive issue identification, no polish
#   R2 (DEEPEN):    evidence grounding + adversarial gap filling
#   R3 (SYNTHESIS): structured final report, tool-limited

from __future__ import annotations

from typing import Optional

from deepreview.prompts.review_agent_prompt import build_review_agent_system_prompt

# ---- Round-specific cognitive-focus headers --------------------------------

_R1_DISCOVER_HEADER = """
## ROUND 1 of 3: DISCOVER Phase

You are conducting the FIRST round of a multi-round review. Your ONLY goal is
to exhaustively identify EVERY potential issue, weakness, strength, and
improvement opportunity in this paper.

CRITICAL RULES for this round:
- Do NOT try to write a polished final report.
- Do NOT worry about formatting, structure, or elegance.
- Use ALL tools freely: pdf_search, pdf_read_lines, pdf_jump, pdf_annotate,
  paper_search, read_paper.
- Create MANY annotations. Target: 15-25 distinct annotated issues.
- Search literature aggressively to establish novelty context.
- Cover EVERY section of the paper (abstract, intro, method, experiments,
  conclusion). No section left unexamined.
- Your output at the end of this round should be: raw annotations + a rough
  list of identified issues, strengths, and weaknesses. This will be deepened
  in Round 2.

IMPORTANT: At the end of this round, the system will check your coverage and
identify any gaps. Round 2 will ask you to fill those gaps.
"""

_R2_DEEPEN_HEADER_TEMPLATE = """
## ROUND 2 of 3: DEEPEN Phase

You are conducting the SECOND round of a multi-round review. Below is your
Round 1 output. Your goal now is to DEEPEN every finding.

CRITICAL RULES for this round:
- For EVERY issue identified in Round 1: find EXACT quoted evidence from the
  paper text. Use pdf_read_lines to verify and extract the relevant passages.
- Search literature (paper_search, read_paper) to contextualize novelty
  claims and compare against related work.
- Assess severity for each issue: critical / major / minor / suggestion.

SECTION COVERAGE MANDATE -- the following sections were MISSING or empty in
Round 1 and MUST be filled in this round:
{missing_sections_formatted}

ADVERSARIAL GAP REPORT -- the following potential critiques were identified as
possibly missed in Round 1. You MUST address each one:
{adversarial_gaps_formatted}

Use all tools freely. Your Round 2 output should be a detailed, evidence-backed
analysis that covers all sections and addresses all gaps.
"""

_R3_SYNTHESIZE_HEADER = """
## ROUND 3 of 3: SYNTHESIS Phase (FINAL)

You are conducting the FINAL round. Below is your deepened Round 2 analysis.
Your goal: produce a polished, structured, internally consistent final review
report.

CRITICAL RULES for this round:
- You may ONLY use the review_final_markdown_write tool. No other tools are
  available in this round.
- Produce a COMPLETE final report covering ALL required sections.
- Cross-check: do the quantitative Scores match the qualitative assessment?
- Cross-check: are all claims from Round 2 represented? No claim should be
  silently dropped.
- Cross-check: are there any internal contradictions? Resolve them.
- Output must be in polished, publication-quality English.
- Use review_final_markdown_write in section mode: submit one section per call.

This is your FINAL output. Make it count.
"""

# ---- Gap check prompt ------------------------------------------------------

_GAP_CHECK_SYSTEM = """You are a meta-reviewer performing an adversarial
coverage audit. Your task: read a review report and identify what the reviewer
may have MISSED.

Be specific. Be concrete. Ground every gap in what the paper text suggests but
the review does not address. Do not fabricate issues that don't exist.

Output exactly 3 bullet points, each starting with "- " and describing one
specific gap. Each bullet should be 1-2 sentences."""


def build_gap_check_user_prompt(
    *,
    paper_markdown: str,
    previous_report: str,
) -> str:
    """Build the user message for the adversarial gap check LLM call."""
    # Truncate paper to first ~8000 chars to control cost
    paper_snippet = str(paper_markdown or "")[:8000]
    report_snippet = str(previous_report or "")[:6000]
    return (
        "Below is a paper (first portion) followed by a review report.\n\n"
        "=== PAPER (excerpt) ===\n"
        f"{paper_snippet}\n\n"
        "=== REVIEW REPORT ===\n"
        f"{report_snippet}\n\n"
        "Identify 3 specific critiques the reviewer may have MISSED."
    )


# ---- Section formatting helpers --------------------------------------------

def _format_missing_sections(missing: list[str] | None) -> str:
    if not missing:
        return "(All required sections were covered in Round 1.)"
    return "\n".join(f"- {s}" for s in missing)


def _format_adversarial_gaps(gaps: str | None) -> str:
    if not gaps or not str(gaps).strip():
        return "(No adversarial gaps identified.)"
    return str(gaps).strip()


# ---- Main exported function ------------------------------------------------

def build_iterative_round_prompt(
    *,
    round_number: int,
    base_paper_markdown: str,
    previous_report: str | None = None,
    adversarial_gaps: str | None = None,
    missing_sections: list[str] | None = None,
    source_file_id: str,
    source_file_name: str,
    ui_language: str = "en",
    paper_search_runtime_state: dict | None = None,
) -> str:
    """Build the full system prompt for a specific iterative round.

    R1: base prompt + DISCOVER header
    R2: base prompt + DEEPEN header (with gaps + missing sections injected)
    R3: base prompt + SYNTHESIS header
    """
    round_num = max(1, min(3, int(round_number or 1)))

    # Build the base prompt (same as single-agent mode)
    base_prompt = build_review_agent_system_prompt(
        source_file_id=source_file_id,
        source_file_name=source_file_name,
        paper_markdown=base_paper_markdown,
        use_meta_review=False,
        paper_search_runtime_state=paper_search_runtime_state,
        ui_language=ui_language,
    )

    if round_num == 1:
        return _R1_DISCOVER_HEADER.strip() + "\n\n" + base_prompt

    prev_text = str(previous_report or "").strip()
    prev_block = (
        f"\n\n---\n## Round {round_num - 1} Output (for reference)\n\n"
        f"{prev_text}\n\n---\n"
    ) if prev_text else ""

    if round_num == 2:
        header = _R2_DEEPEN_HEADER_TEMPLATE.format(
            missing_sections_formatted=_format_missing_sections(missing_sections),
            adversarial_gaps_formatted=_format_adversarial_gaps(adversarial_gaps),
        )
        return header.strip() + prev_block + "\n\n" + base_prompt

    # round_num == 3
    return _R3_SYNTHESIZE_HEADER.strip() + prev_block + "\n\n" + base_prompt


__all__ = [
    "build_iterative_round_prompt",
    "build_gap_check_user_prompt",
    "_GAP_CHECK_SYSTEM",
]