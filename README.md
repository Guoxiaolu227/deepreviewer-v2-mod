<div align="center">

# DeepReviewer-v2 Mod

> **Modified fork** of [DeepReviewer-v2](https://github.com/bytedance/DeepReviewer) (ACL 2025) — a cloud-native, iterative paper review pipeline with self-consistency experiments.

[![Base](https://img.shields.io/badge/base-DeepReviewer--v2%20v0.1.0-1f6feb?style=flat-square)](https://aclanthology.org/2025.acl-long.1420/)
[![Mod Version](https://img.shields.io/badge/version-v0.3.0--dev-orange?style=flat-square)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg?style=flat-square)](./DeepReviewer-v2/LICENSE)
[![LLM](https://img.shields.io/badge/LLM-DeepSeek--v4--pro-6c5ce7?style=flat-square)](https://deepseek.com)

</div>

---

## Overview

This project adapts the open-source DeepReviewer-v2 system for **lightweight local experimentation** — no GPU, no vector DB, no heavy infrastructure. All three layers run via cloud APIs:

| Layer | Original | This Mod |
|:---|:---|:---|
| **LLM Reasoning** | OpenAI-compatible gateway | **DeepSeek-v4-pro** |
| **PDF Parsing** | MinerU (local or API) | **MinerU API v4** |
| **Paper Search** | PASA (local vector DB) | **DeepXiv SDK** |

On top of the baseline, we add an **iterative 3-round pipeline**, a **cost-tracking module**, and a **self-consistency experiment framework**.

```
PDF → MinerU Markdown → [R1 Discover → R2 Deepen → R3 Synthesize] → Final Report (MD + PDF)
```

---

## Features

### Iterative 3-Round Pipeline

| Round | Role | Tools | Goal |
|:---|:---|:---|:---|
| **R1 · Discover** | Exhaustive finder | All tools | Enumerate every issue, produce raw annotation list |
| **R2 · Deepen** | Deepener | All tools | Back each claim with source-line citations, fill missing sections |
| **R3 · Synthesize** | Synthesizer | `review_final_markdown_write` only | Cross-validate, merge overlaps, output polished report |

An **adversarial gap check** runs between R1 and R2 to detect up to 3 missing review angles.

### Cost Tracking (`cost.py`)

- DeepSeek V4 pricing baked in: v4-pro (¥3 / ¥6 per 1M in/out), v4-flash (¥1 / ¥2)
- Per-phase accounting: `mineru_parse`, `iter_round_1/2/3`, `agent_run_N`, `meta_review_merge`
- Outputs `cost_breakdown.json` + `cost_breakdown.md`

### Experiment Framework (`experiment/`)

- **metrics.py**: `claim_overlap` (token-Jaccard, threshold 0.25), `section_completeness` (11-section rubric)
- **reporter.py**: Markdown report generation
- **CLI**: `python main.py experiment --pdf paper.pdf`

### Prompt Optimization

- Review agent prompt reduced by **~70% token consumption** vs upstream
- Chinese-first output constraint for all user-facing annotations

---

## Version

| Artifact | Version | Notes |
|:---|:---|:---|
| **This mod** | `v0.3.0-dev` | Iterative pipeline + cost tracking + experiment framework |
| **Base (upstream)** | `v0.1.0` | DeepReviewer-v2 as of 2026-06 |

> ⏳ **Active development.** See [Roadmap](#roadmap) for planned work.

---

## Experiment Results

### tool.pdf (658 KB, deepseek-v4-pro)

| Strategy | Self-Consistency | Section Coverage | Tokens | Cost (¥) |
|:---|:---:|:---:|:---:|:---:|
| **Baseline** | 22.1% | 7.5 / 11 | ~57K | 0.21 |
| Parallel (N=3) | 9.0% | 5.5 / 11 | ~322K | 0.95 |
| **Iterative (3R)** | 13.8% | 7.5 / 11 | ~237K | 0.70 |

> ⚠️ Prior experiments on APERS.pdf (3.1 MB) achieved 30% self-consistency with Parallel. The tool.pdf corpus is too small for conclusive results. A re-run on APERS.pdf is the immediate next step.

---

## Quick Start

### 1) Environment

```bash
cd DeepReviewer-v2
python -m venv ../.venv
../.venv/Scripts/activate     # Windows
# source ../.venv/bin/activate  # macOS / Linux
pip install -e .
```

### 2) Configuration

```bash
cp .env.example .env
```

Fill in the `.env` file:

```ini
# LLM — DeepSeek
BASE_URL=https://api.deepseek.com/v1
OPENAI_API_KEY=sk-your-key
AGENT_MODEL=deepseek-v4-pro

# PDF Parsing — MinerU
MINERU_API_TOKEN=your-mineru-token

# Paper Search — DeepXiv
PAPER_SEARCH_ENABLED=true
PAPER_SEARCH_PROVIDER=deepxiv
DEEPXIV_API_TOKEN=your-deepxiv-token
DEEPXIV_RETRIEVE_TOP_K=8

# Enable iterative pipeline
ENABLE_ITERATIVE_REVIEW=true
ITERATIVE_ROUNDS=3
```

### 3) Run a Review

```bash
# Single review (baseline or iterative, controlled by config)
python main.py submit --pdf test/tool.pdf
python main.py watch --job-id <job_id> --timeout 1800
python main.py result --job-id <job_id> --format all

# Self-consistency experiment
python main.py experiment --pdf test/tool.pdf
```

---

## Project Structure

```
deepreviewer-v2-mod/
├── DeepReviewer-v2/
│   ├── deepreview/
│   │   ├── prompts/
│   │   │   ├── review_agent_prompt.py        # Baseline prompt (optimized, -70% tokens)
│   │   │   └── iterative_agent_prompt.py     # 3-round iterative prompts
│   │   ├── experiment/
│   │   │   ├── metrics.py                    # Self-consistency & section metrics
│   │   │   └── reporter.py                   # Experiment report generation
│   │   ├── cost.py                           # Token-to-cost tracking
│   │   ├── runner.py                         # Core pipeline (baseline + iterative)
│   │   ├── config.py                         # Settings (incl. iterative flags)
│   │   └── ...
│   ├── pasa/                                 # PASA fallback (not required)
│   ├── test/                                 # Test PDFs
│   ├── test_report/                          # Generated review reports (Markdown)
│   └── pyproject.toml
├── test_report/                              # Final PDF reports
├── STATE.md                                  # Current development state + known bugs
├── 复现DeepReviewer-v2.md                     # Full reproduction diary (Chinese)
└── README.md
```

---

## Known Issues

| Issue | Impact | Status |
|:---|:---|:---:|
| Token tracking returns 0 for baseline / iterative | Cost table all zeros; only parallel has real data | ⚠️ |
| `_run_single_agent_instance` skips `_consume` callback | Agent-cancelled via tool call misses token reporting | ⚠️ |
| Parallel self-consistency degrades (9% vs prior 30%) | Needs investigation on corpus size / prompt drift | ⚠️ |
| matplotlib not installed | No charts in experiment reports | ⚠️ |
| GBK encoding breaks Chinese console output | Log readability | ⚠️ |

---

## Roadmap

- [x] **v0.1.0** — Local reproduction with DeepSeek + MinerU API + DeepXiv
- [x] **v0.2.0** — Prompt optimization (-70% tokens), simplified agent prompt
- [x] **v0.3.0** — Iterative 3-round pipeline (Discover → Deepen → Synthesize)
- [ ] **v0.3.1** — Fix token tracking bug, re-run on APERS.pdf
- [ ] **v0.4.0** — Multi-model benchmarks (v4-pro vs v4-flash vs reasoner)
- [ ] **v0.5.0** — Meta-review: aggregate & reconcile multi-pass reviews

---

## Reproduction Notes

The full journey — environment setup, Git proxy, dependency hell, MinerU 401 errors, DeepXiv 404, agent tool-use failures — is documented in:

📄 **[复现DeepReviewer-v2.md](./复现DeepReviewer-v2.md)** (Chinese)

---

## Citation

```bibtex
@inproceedings{zhu-etal-2025-deepreview,
    title     = "{DeepReview: Improving LLM-based Paper Review with Human-like Deep Thinking Process}",
    author    = "Zhu, Minjun and Weng, Yixuan and Yang, Linyi and Zhang, Yue",
    booktitle = "Proceedings of the 63rd Annual Meeting of the ACL (Volume 1: Long Papers)",
    year      = "2025",
    publisher = "Association for Computational Linguistics",
    doi       = "10.18653/v1/2025.acl-long.1420",
}
```

---

## License

MIT — see [`DeepReviewer-v2/LICENSE`](./DeepReviewer-v2/LICENSE) and [`DeepReviewer-v2/THIRD_PARTY_NOTICES.md`](./DeepReviewer-v2/THIRD_PARTY_NOTICES.md).
