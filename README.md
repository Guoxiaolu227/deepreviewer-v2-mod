<div align="center">

# DeepReviewer-v2 Mod

> ⚡ **Modified fork** of [DeepReviewer-v2](https://github.com/bytedance/DeepReviewer) — ACL 2025 paper review system with custom experiment pipeline.

[![Base: DeepReviewer-v2](https://img.shields.io/badge/base-DeepReviewer--v2%20v0.1.0-1f6feb?style=flat-square)](https://aclanthology.org/2025.acl-long.1420/)
[![Mod Version](https://img.shields.io/badge/mod-v0.1.0-orange?style=flat-square)]()
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg?style=flat-square)](./DeepReviewer-v2/LICENSE)

</div>

---

## What Is This

This repository contains a **modified version of DeepReviewer-v2**, adapted for local reproduction and experimentation with a cloud-native API-driven tech stack:

| Layer | Original | Our Mod |
| :--- | :--- | :--- |
| **LLM Reasoning** | OpenAI-compatible gateway | **DeepSeek-v4-pro** (deepseek-reasoner) |
| **PDF Parsing** | MinerU (local / API) | **MinerU API v4** (cloud) |
| **Paper Search** | PASA (local vector DB) | **DeepXiv SDK** (cloud retrieval API) |

The goal is to run the full review pipeline **without heavy local infrastructure** (no GPU, no vector DB), making it lightweight enough for a single graduate student's workstation.

---

## Version

| Artifact | Version | Notes |
| :--- | :--- | :--- |
| **This mod** | 0.1.0 | Initial reproduction & baseline experiments complete |
| **Base (DeepReviewer-v2)** | 0.1.0 | Upstream as of 2026-06 |

> ⏳ **Status: Active development.** Future updates will refine prompts, add new experiment baselines, and improve the meta-review layer. See [Roadmap](#roadmap) below.

---

## Project Structure

`
deepreviewer-v2-mod/
├── DeepReviewer-v2/          # Modified upstream source
│   ├── deepreview/           # Core pipeline (review agent, tools, reports)
│   ├── pasa/                 # PASA paper-search service (fallback)
│   ├── test/                 # Test PDFs used in experiments
│   ├── test_report/          # Generated review reports (Markdown)
│   ├── scripts/              # Build & release scripts
│   └── pyproject.toml        # Package metadata (v0.1.0)
├── test_report/              # Experiment output: final PDF reports
├── 复现DeepReviewer-v2.md     # Full reproduction diary (Chinese)
└── README.md                 # This file
`

---

## Quick Start

### 1) Environment

`ash
cd DeepReviewer-v2
python -m venv ../.venv
../.venv/Scripts/activate    # Windows
pip install -e .
`

### 2) Configuration

`ash
cp .env.example .env
# Fill in: OPENAI_API_KEY (DeepSeek key), MINERU_API_TOKEN, DEEPXIV_API_TOKEN
`

### 3) Submit a Paper

`ash
python main.py submit --pdf test/tool.pdf
python main.py watch --job-id <job_id> --timeout 1800
python main.py result --job-id <job_id> --format all
`

For detailed configuration and troubleshooting, see DeepReviewer-v2/README.zh-CN.md.

---

## Reproduction Notes

The full reproduction journey — from zero to a working pipeline, including all pitfalls (Git proxy, dependency hell, MinerU 401, DeepXiv 404, Agent tool-use failures, gate enforcement) — is documented in:

📄 **[复现DeepReviewer-v2.md](./复现DeepReviewer-v2.md)** (Chinese)

Experiment outputs comparing the baseline with our modified pipeline are under 	est_report/.

---

## Roadmap

- [x] **v0.1.0** — Local reproduction with DeepSeek + MinerU API + DeepXiv
- [ ] **v0.2.0** — Prompt engineering: refine review quality & consistency
- [ ] **v0.3.0** — Meta-review layer: aggregate multi-pass reviews
- [ ] **v0.4.0** — Comparative experiments: multi-model + multi-provider benchmarks

---

## Citation

If you use DeepReviewer in your research:

`ibtex
@inproceedings{zhu-etal-2025-deepreview,
    title = ""{D}eep{R}eview: Improving {LLM}-based Paper Review with Human-like Deep Thinking Process"",
    author = ""Zhu, Minjun  and Weng, Yixuan  and Yang, Linyi  and Zhang, Yue"",
    booktitle = ""Proceedings of the 63rd Annual Meeting of the ACL (Volume 1: Long Papers)"",
    year = ""2025"",
    publisher = ""Association for Computational Linguistics"",
    doi = ""10.18653/v1/2025.acl-long.1420"",
}
`

---

## License

MIT — see DeepReviewer-v2/LICENSE and DeepReviewer-v2/THIRD_PARTY_NOTICES.md.
