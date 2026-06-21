# meta_review.py -- Parallel review merge via meta-reviewer LLM.
#
# Strategy:
#   1. N independent Agent Loops each produce a full review report (.md)
#   2. A meta-reviewer LLM reads all N reports and produces a single
#      consolidated report:
#      - Issues confirmed by >=2 reviewers:  promote, cite source reports.
#      - Issues reported by only 1 reviewer: keep if well-argued, mark [single-source].
#      - Conflicting judgments: preserve as [disputed] with both positions.
#      - Sections present in some reports but missing in others: fill from available.
#
# Output format: same 11-section markdown as standard final report.

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from deepreview.config import Settings, get_settings
from deepreview.report.final_report import validate_final_report
from deepreview.storage import write_text_atomic


# ---- Data structures --------------------------------------------------------

@dataclass
class ReviewRunResult:
    """Output of a single parallel review agent run."""
    run_index: int
    report_markdown: str
    annotation_count: int
    paper_search_total_calls: int
    paper_search_distinct_queries: int
    token_usage: dict = field(default_factory=dict)
    tool_usage: dict = field(default_factory=dict)


@dataclass
class MetaReviewResult:
    """Output of the meta-review merge."""
    consolidated_markdown: str
    run_results: list
    merge_token_usage: dict = field(default_factory=dict)
    confirmed_count: int = 0
    single_source_count: int = 0
    disputed_count: int = 0
# ---- Prompt construction ----------------------------------------------------

_META_REVIEW_SYSTEM_PROMPT = """You are a senior area chair performing meta-review consolidation.

You will receive {num_reports} independent review reports for the SAME paper.
Each report was produced by a separate reviewer who used PDF reading tools,
literature search, and annotation tools to ground their analysis.

Your task: produce a SINGLE consolidated review report (in English, Markdown)
that synthesizes all {num_reports} reviews intelligently.

RULES:
1. IDENTIFY CONSENSUS: If 2+ reviewers mention the same issue (same claim,
   similar reasoning), it is CONFIRMED. Promote it prominently. Cite which
   reviewers agree (e.g., "[R1,R3 agree]").

2. HANDLE SINGLE-SOURCE CLAIMS: If only one reviewer raises an issue, evaluate
   its reasoning quality. If well-argued with evidence from the paper, KEEP it
   but mark as "[single-source: Rn]". If poorly argued, OMIT or group into
   "Minor Observations".

3. HANDLE CONFLICTS: If reviewers disagree on a judgment, do NOT pick a winner.
   Present both positions with reasoning as "[DISPUTED] Rn: ... vs Rm: ...".

4. FILL GAPS: If a section is missing from some reports, use content from
   the reports that DO have it. Do not fabricate.

5. DEDUPLICATE: Merge similar observations. Prefer the most precise formulation.

6. OUTPUT FORMAT: Produce exactly these sections as Markdown headings:
   ## Summary
   ## Strengths
   ## Weaknesses
   ## Key Issues
   ## Actionable Suggestions
   ## Storyline Options + Writing Outlines
   ## Priority Revision Plan
   ## Experiment Inventory & Research Experiment Plan
   ## Novelty Verification & Related-Work Matrix
   ## References
   ## Scores

7. At the end, append "## Meta-Review Notes" documenting:
   - Number of confirmed/single-source/disputed claims
   - Any significant differences between reviewers
   - Overall reviewer agreement level (High / Medium / Low)

8. Write in English only. Be specific and evidence-grounded."""


def build_meta_review_user_prompt(
    *,
    paper_title: str,
    run_results: list,
) -> str:
    """Construct the user message containing all N reports."""
    n = len(run_results)
    blocks = [
        f"# Paper: {paper_title}",
        "",
        f"Below are {n} independent review reports.",
        "Each begins with a run header for provenance tracking.",
        "",
    ]
    for rr in run_results:
        blocks.append("---")
        blocks.append(f"## Review Run #{rr.run_index + 1}")
        blocks.append("")
        blocks.append(f"- Annotations: {rr.annotation_count}")
        blocks.append(f"- Paper search calls: {rr.paper_search_total_calls}")
        blocks.append(f"- Distinct queries: {rr.paper_search_distinct_queries}")
        blocks.append("")
        blocks.append(rr.report_markdown)
        blocks.append("")
    blocks.append("---")
    blocks.append("Now produce the consolidated meta-review as instructed.")
    return "\n".join(blocks)

# ---- LLM merge --------------------------------------------------------------

def _resolve_meta_review_model(settings: Settings) -> str:
    """Use dedicated meta_review_model if set, otherwise fallback to agent_model."""
    dedicated = str(settings.meta_review_model or "").strip()
    if dedicated:
        return dedicated
    return str(settings.agent_model or "gpt-5.2").strip()


def _build_meta_review_client(settings: Settings) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=str(settings.openai_api_key or "EMPTY"),
        base_url=settings.openai_base_url,
        timeout=300,
    )


async def merge_reports(
    *,
    paper_title: str,
    run_results: list,
    settings: Settings,
) -> MetaReviewResult:
    """Merge N review reports into one consolidated report via LLM meta-review."""
    if len(run_results) < 2:
        if run_results:
            return MetaReviewResult(
                consolidated_markdown=run_results[0].report_markdown,
                run_results=run_results,
            )
        return MetaReviewResult(consolidated_markdown="", run_results=[])

    client = _build_meta_review_client(settings)
    model = _resolve_meta_review_model(settings)

    system_prompt = _META_REVIEW_SYSTEM_PROMPT.format(num_reports=len(run_results))
    user_prompt = build_meta_review_user_prompt(
        paper_title=paper_title,
        run_results=run_results,
    )

    response = await client.chat.completions.create(
        model=model,
        temperature=settings.meta_review_temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    consolidated = str(response.choices[0].message.content or "").strip()

    usage = {}
    if response.usage:
        usage = {
            "requests": 1,
            "input_tokens": response.usage.prompt_tokens or 0,
            "output_tokens": response.usage.completion_tokens or 0,
            "total_tokens": response.usage.total_tokens or 0,
        }

    confirmed_count = len(re.findall(r"\[R\d+,R\d+", consolidated))
    single_source_count = len(re.findall(r"\[single-source:", consolidated))
    disputed_count = len(re.findall(r"\[DISPUTED\]", consolidated))

    validation = validate_final_report(
        markdown=consolidated,
        min_english_words=settings.min_english_words_for_final,
        min_chinese_chars=settings.min_chinese_chars_for_final,
        force_english_output=settings.force_english_output,
    )

    if not validation.ok and validation.missing_sections:
        consolidated += (
            "\n\n---"
            "\n**Meta-Review Note:** The following expected sections were not "
            "fully covered by any reviewer and remain absent: "
            + ", ".join(validation.missing_sections)
            + "."
        )

    return MetaReviewResult(
        consolidated_markdown=consolidated,
        run_results=run_results,
        merge_token_usage=usage,
        confirmed_count=confirmed_count,
        single_source_count=single_source_count,
        disputed_count=disputed_count,
    )


# ---- Persistence helpers ----------------------------------------------------

def save_individual_report(
    *,
    job_dir: Path,
    run_index: int,
    report_markdown: str,
) -> Path:
    """Save one parallel run report to job_dir/final_report_run_{i}.md."""
    path = job_dir / f"final_report_run_{run_index + 1}.md"
    write_text_atomic(path, report_markdown)
    return path


def save_consolidated_report(
    *,
    job_dir: Path,
    report_markdown: str,
    is_final: bool = True,
) -> Path:
    """Save consolidated report. If is_final, also write to final_report.md."""
    consolidated_path = job_dir / "final_report_consolidated.md"
    write_text_atomic(consolidated_path, report_markdown)
    if is_final:
        final_path = job_dir / "final_report.md"
        write_text_atomic(final_path, report_markdown)
    return consolidated_path
