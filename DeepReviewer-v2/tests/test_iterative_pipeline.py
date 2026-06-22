# test_iterative_pipeline.py -- Tests for the iterative 3-round review pipeline.

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---- Helpers ---------------------------------------------------------------

def _dummy_usage():
    return SimpleNamespace(requests=1, input_tokens=100, output_tokens=50, total_tokens=150)


def _make_fake_run_result(markdown: str, run_index: int = 0):
    """Create a fake ReviewRunResult that _run_single_agent_instance returns."""
    return SimpleNamespace(
        run_index=run_index,
        report_markdown=markdown,
        annotation_count=5,
        paper_search_total_calls=2,
        paper_search_distinct_queries=1,
        token_usage={"requests": 2, "input_tokens": 5000, "output_tokens": 2000, "total_tokens": 7000},
        tool_usage={"pdf_read_lines": 3, "pdf_annotate": 2},
    )


# ---- Test: iterative round prompts produce distinct output -----------------

def test_build_iterative_round_prompt():
    """R1/R2/R3 prompts are distinct and contain expected content."""
    from deepreview.prompts.iterative_agent_prompt import build_iterative_round_prompt

    paper_md = "# Test Paper\n\nThis is a test paper about machine learning."

    p1 = build_iterative_round_prompt(
        round_number=1, base_paper_markdown=paper_md,
        source_file_id="test", source_file_name="test.pdf",
    )
    assert "DISCOVER" in p1, "R1 should contain DISCOVER"
    assert "DEEPEN" not in p1, "R1 should NOT contain DEEPEN"

    p2 = build_iterative_round_prompt(
        round_number=2, base_paper_markdown=paper_md,
        previous_report="## Summary\nR1 found issues.",
        adversarial_gaps="- Gap 1: missing X\n- Gap 2: missing Y",
        missing_sections=["Novelty Verification"],
        source_file_id="test", source_file_name="test.pdf",
    )
    assert "DEEPEN" in p2, "R2 should contain DEEPEN"
    assert "Gap 1" in p2 or "missing X" in p2, "R2 should contain gap text"
    assert "Novelty Verification" in p2, "R2 should mention missing sections"

    p3 = build_iterative_round_prompt(
        round_number=3, base_paper_markdown=paper_md,
        previous_report="## Summary\nDeepened analysis.",
        source_file_id="test", source_file_name="test.pdf",
    )
    assert "SYNTHESIS" in p3, "R3 should contain SYNTHESIS"
    assert "review_final_markdown_write" in p3.lower(), "R3 should mention write tool"


# ---- Test: gap check prompt ------------------------------------------------

def test_gap_check_prompt():
    from deepreview.prompts.iterative_agent_prompt import (
        _GAP_CHECK_SYSTEM,
        build_gap_check_user_prompt,
    )
    paper = "This paper is about topic X."
    report = "## Summary\nThe paper is fine."
    user = build_gap_check_user_prompt(paper_markdown=paper, previous_report=report)
    assert paper in user
    assert report in user
    assert len(_GAP_CHECK_SYSTEM) > 10


# ---- Test: full iterative pipeline (mocked) --------------------------------

def test_iterative_pipeline_routing():
    """Verify config flags route to iterative pipeline."""
    from deepreview.config import Settings

    s = Settings()
    assert s.enable_iterative_review is False
    assert s.iterative_rounds == 3
    assert s.iterative_model == ""

    s2 = Settings(ENABLE_ITERATIVE_REVIEW="true", ITERATIVE_ROUNDS="4")
    assert s2.enable_iterative_review is True
    assert s2.iterative_rounds == 4


# ---- Test: experiment metrics ----------------------------------------------

def test_compute_claim_overlap_identical():
    from deepreview.experiment.metrics import compute_claim_overlap
    r = "## Summary\nThis paper proposes a novel approach for text classification.\n\n## Strengths\nRigorous evaluation. Clear writing."
    assert compute_claim_overlap(r, r) == 1.0


def test_compute_claim_overlap_different():
    from deepreview.experiment.metrics import compute_claim_overlap
    r1 = "## Summary\nClassification method using transformers."
    r2 = "## Summary\nImage segmentation using convolutional networks on medical data."
    assert compute_claim_overlap(r1, r2) < 0.3


def test_compute_section_completeness():
    from deepreview.experiment.metrics import compute_section_completeness
    r = "## Summary\nTest.\n\n## Strengths\nGood.\n\n## Weaknesses\nBad.\n\n## Scores\n7/10."
    sc = compute_section_completeness(r)
    assert sc["_non_empty_count"] >= 3


def test_compute_all_metrics():
    from deepreview.experiment.metrics import compute_all_metrics
    r1 = "## Summary\nMethod A.\n\n## Strengths\nGood.\n\n## Weaknesses\nLimited."
    r2 = "## Summary\nMethod A variant.\n\n## Strengths\nVery good.\n\n## Weaknesses\nLimited scope."
    m = compute_all_metrics({"baseline_v1": r1, "baseline_v2": r2})
    assert len(m.run_ids) == 2
    assert m.claim_overlap_matrix["baseline_v1"]["baseline_v2"] > 0


# ---- Test: experiment reporter ---------------------------------------------

def test_generate_report(tmp_path):
    from deepreview.experiment.metrics import compute_all_metrics
    from deepreview.experiment.reporter import generate_experiment_report

    r1 = "## Summary\nMethod A.\n\n## Strengths\nGood.\n\n## Weaknesses\nLimited."
    r2 = "## Summary\nMethod A refined.\n\n## Strengths\nExcellent.\n\n## Weaknesses\nSome limits."
    m = compute_all_metrics({"baseline_v1": r1, "baseline_v2": r2}, costs={"baseline_v1": 0.1, "baseline_v2": 0.12})

    path = generate_experiment_report(m, output_dir=tmp_path, title="Test")
    assert path.exists()
    content = path.read_text()
    assert "Test" in content
    assert "baseline_v1" in content
