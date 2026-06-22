# experiment/reporter.py -- Experiment report generation and charting.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from deepreview.experiment.metrics import (
    ExperimentMetrics,
    _REQUIRED_SECTION_GROUPS,
)


# ---- Markdown report -------------------------------------------------------

def _report_header(title: str, paper_name: str, model: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"# {title}\n\n"
        f"**论文**: {paper_name}  |  **模型**: {model}  |  **日期**: {now}\n\n"
        "---\n\n"
    )


def _run_summary_table(metrics: ExperimentMetrics) -> str:
    lines = [
        "## 运行总览",
        "",
        "| 策略 | 运行 | 输入Token | 输出Token | 总Token | 成本(¥) | Section数 |",
        "|------|------|----------|----------|---------|---------|----------|",
    ]
    strategy_order = ["baseline", "parallel", "iterative"]
    ordered = []
    for prefix in strategy_order:
        ordered.extend([rid for rid in metrics.run_ids if rid.startswith(prefix)])
    ordered.extend([rid for rid in metrics.run_ids if rid not in ordered])

    for rid in ordered:
        tu = metrics.token_usage.get(rid, {})
        inp = tu.get("input_tokens", tu.get("input", 0))
        out = tu.get("output_tokens", tu.get("output", 0))
        tot = tu.get("total_tokens", inp + out)
        cost = metrics.costs.get(rid, 0)
        sc = metrics.section_counts.get(rid, 0)
        lines.append(
            f"| {rid} | {rid.rsplit('_',1)[-1]} | {inp:,} | {out:,} | "
            f"{tot:,} | {cost:.4f} | {sc}/11 |"
        )

    return "\n".join(lines) + "\n"


def _consistency_table(metrics: ExperimentMetrics) -> str:
    """Build the self-consistency comparison table."""
    strategies = []
    for prefix in ["baseline", "parallel", "iterative"]:
        runs = [r for r in metrics.run_ids if r.startswith(prefix)]
        if runs:
            strategies.append((prefix, runs))

    lines = [
        "## 自一致性核心结果",
        "",
        "| 策略 | 组内一致性 | 组内词级Jaccard | Section完整度 | 成本(¥) | 一致性/¥ |",
        "|------|-----------|----------------|-------------|---------|----------|",
    ]

    for prefix, runs in strategies:
        cons = metrics.strategy_self_consistency(prefix) or 0
        jac = _avg_jaccard(metrics, prefix) or 0
        sc = metrics.strategy_avg_section_count(prefix) or 0
        cost = metrics.strategy_avg_cost(prefix) or 0
        eff = cons / cost if cost > 0 else 0
        lines.append(
            f"| {prefix.title()} | **{cons:.1%}** | {jac:.3f} | "
            f"{sc:.1f}/11 | {cost:.4f} | {eff:.3f} |"
        )

    return "\n".join(lines) + "\n"


def _avg_jaccard(metrics: ExperimentMetrics, prefix: str) -> float | None:
    runs = [r for r in metrics.run_ids if r.startswith(prefix)]
    if len(runs) < 2:
        return None
    vals = []
    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            v = metrics.word_jaccard_matrix.get(runs[i], {}).get(runs[j])
            if v is not None:
                vals.append(v)
    return sum(vals) / len(vals) if vals else None


def _cross_consistency_table(metrics: ExperimentMetrics) -> str:
    lines = [
        "## 交叉一致性矩阵 (Claim Overlap)",
        "",
    ]
    if not metrics.run_ids:
        return "\n".join(lines) + "*No data.*\n"

    header = "| | " + " | ".join(metrics.run_ids) + " |"
    sep = "|" + "|".join(["---"] * (len(metrics.run_ids) + 1)) + "|"
    lines.append(header)
    lines.append(sep)
    for ri in metrics.run_ids:
        row = f"| **{ri}** |"
        for rj in metrics.run_ids:
            v = metrics.claim_overlap_matrix.get(ri, {}).get(rj, 0)
            row += f" {v:.1%} |"
        lines.append(row)
    return "\n".join(lines) + "\n"


def _section_completeness_table(metrics: ExperimentMetrics) -> str:
    lines = [
        "## Section 完整性",
        "",
    ]
    header = "| Section | " + " | ".join(metrics.run_ids) + " |"
    sep = "|" + "|".join(["---"] * (len(metrics.run_ids) + 1)) + "|"
    lines.append(header)
    lines.append(sep)
    for label, _ in _REQUIRED_SECTION_GROUPS:
        row = f"| {label} |"
        for rid in metrics.run_ids:
            sc = metrics.section_completeness.get(rid, {})
            wc = sc.get(label, 0)
            row += f" {wc:,} |"
        lines.append(row)

    # Non-empty count row
    row = "| **非空总数** |"
    for rid in metrics.run_ids:
        row += f" **{metrics.section_counts.get(rid, 0)}/11** |"
    lines.append(row)

    return "\n".join(lines) + "\n"


def _conclusion(metrics: ExperimentMetrics) -> str:
    lines = ["## 结论", ""]
    base_cons = metrics.strategy_self_consistency("baseline") or 0
    par_cons = metrics.strategy_self_consistency("parallel") or 0
    iter_cons = metrics.strategy_self_consistency("iterative") or 0

    if iter_cons > 0:
        if iter_cons > par_cons:
            pct = (iter_cons - par_cons) / max(par_cons, 0.01) * 100
            lines.append(
                f"✅ **迭代方案自一致性 ({iter_cons:.1%}) 优于并行方案 ({par_cons:.1%})**，"
                f"提升 {pct:.0f}%。"
            )
        else:
            lines.append(
                f"迭代方案自一致性 ({iter_cons:.1%}) 未超过并行方案 ({par_cons:.1%})。"
                "建议检查 prompt 设计和轮次配置。"
            )

        base_cost = metrics.strategy_avg_cost("baseline") or 0
        par_cost = metrics.strategy_avg_cost("parallel") or 0
        iter_cost = metrics.strategy_avg_cost("iterative") or 0
        lines.append("")
        lines.append(f"- Baseline 成本: ¥{base_cost:.4f}")
        lines.append(f"- Parallel 成本: ¥{par_cost:.4f}")
        lines.append(f"- Iterative 成本: ¥{iter_cost:.4f}")

        # Token efficiency
        if iter_cost > 0 and par_cost > 0:
            iter_eff = iter_cons / iter_cost
            par_eff = par_cons / par_cost
            lines.append(f"- Iterative 单位成本一致性: {iter_eff:.3f}")
            lines.append(f"- Parallel 单位成本一致性: {par_eff:.3f}")
            if iter_eff > par_eff:
                lines.append(f"- **Iterative 的 token 效率是 Parallel 的 {iter_eff/par_eff:.1f}x**")

    return "\n".join(lines) + "\n"


def generate_experiment_report(
    metrics: ExperimentMetrics,
    *,
    output_dir: str | Path,
    title: str = "自一致性对比实验报告",
    paper_name: str = "unknown.pdf",
    model: str = "unknown",
) -> Path:
    """Generate the full experiment report as Markdown.

    Returns the path to the generated report.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sections = [
        _report_header(title, paper_name, model),
        _run_summary_table(metrics),
        _consistency_table(metrics),
        _cross_consistency_table(metrics),
        _section_completeness_table(metrics),
        _conclusion(metrics),
    ]

    report_path = output_dir / "experiment_report.md"
    report_path.write_text("\n".join(sections), encoding="utf-8")
    return report_path


# ---- Chart generation (matplotlib, optional) -------------------------------

def _try_import_matplotlib() -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        return True
    except ImportError:
        return False


def generate_charts(
    metrics: ExperimentMetrics,
    output_dir: str | Path,
) -> list[Path]:
    """Generate all experiment charts. Silently skips if matplotlib unavailable.

    Returns list of generated chart paths.
    """
    if not _try_import_matplotlib():
        return []

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    output_dir = Path(output_dir)
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    # Try to set Chinese font
    try:
        plt.rcParams["font.sans-serif"] = ["SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
    except Exception:
        pass

    # ---- 1. Consistency bar chart ----
    try:
        fig, ax = plt.subplots(figsize=(8, 5))
        strategies = [("Baseline", "baseline"), ("Parallel(N=3)", "parallel"), ("Iterative(3R)", "iterative")]
        labels = []
        values = []
        for label, prefix in strategies:
            cons = metrics.strategy_self_consistency(prefix)
            if cons is not None:
                labels.append(label)
                values.append(cons * 100)
        colors = ["#d62728", "#ff7f0e", "#2ca02c"][:len(labels)]
        bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=0.8)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{val:.1f}%", ha="center", va="bottom", fontweight="bold")
        ax.set_ylabel("Claim Overlap (%)")
        ax.set_title("Self-Consistency by Strategy")
        ax.set_ylim(0, max(values) * 1.3 if values else 100)
        ax.grid(axis="y", alpha=0.3)
        path = charts_dir / "consistency_bar.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        generated.append(path)
    except Exception:
        pass

    # ---- 2. Cost comparison bar chart ----
    try:
        fig, ax = plt.subplots(figsize=(8, 5))
        cost_labels = []
        cost_values = []
        for label, prefix in strategies:
            c = metrics.strategy_avg_cost(prefix)
            if c is not None:
                cost_labels.append(label)
                cost_values.append(c)
        colors2 = ["#d62728", "#ff7f0e", "#2ca02c"][:len(cost_labels)]
        bars = ax.bar(cost_labels, cost_values, color=colors2, edgecolor="white", linewidth=0.8)
        for bar, val in zip(bars, cost_values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(cost_values) * 0.01,
                    f"¥{val:.4f}", ha="center", va="bottom", fontweight="bold")
        ax.set_ylabel("Cost (CNY)")
        ax.set_title("Average Cost per Strategy")
        ax.grid(axis="y", alpha=0.3)
        path = charts_dir / "cost_comparison.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        generated.append(path)
    except Exception:
        pass

    # ---- 3. Token efficiency scatter ----
    try:
        fig, ax = plt.subplots(figsize=(8, 5))
        for label, prefix, color in zip(
            ["Baseline", "Parallel(N=3)", "Iterative(3R)"],
            ["baseline", "parallel", "iterative"],
            ["#d62728", "#ff7f0e", "#2ca02c"],
        ):
            cons = metrics.strategy_self_consistency(prefix)
            cost = metrics.strategy_avg_cost(prefix)
            if cons is not None and cost is not None and cost > 0:
                ax.scatter(cost, cons * 100, c=color, s=120, label=label, zorder=5)
                ax.annotate(f"{cons:.1%}", (cost, cons * 100),
                           textcoords="offset points", xytext=(8, 4), fontsize=9)
        ax.set_xlabel("Cost (CNY)")
        ax.set_ylabel("Claim Overlap (%)")
        ax.set_title("Token Efficiency: Consistency per Cost")
        ax.legend()
        ax.grid(alpha=0.3)
        path = charts_dir / "token_efficiency.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        generated.append(path)
    except Exception:
        pass

    # ---- 4. Section completeness radar (true spider chart) ----
    try:
        section_labels = [label for label, _ in _REQUIRED_SECTION_GROUPS]
        n_sections = len(section_labels)

        # Abbreviate long labels for radar display
        label_abbr = {
            'Storyline Options + Writing Outlines': 'Storyline\n& Outlines',
            'Priority Revision Plan': 'Priority\nRevision',
            'Experiment Inventory & Research Experiment Plan': 'Experiment\nPlan',
            'Novelty Verification & Related-Work Matrix': 'Novelty &\nRelated Work',
            'Actionable Suggestions': 'Actionable\nSuggestions',
        }
        short_labels = [label_abbr.get(l, l) for l in section_labels]

        angles = np.linspace(0, 2 * np.pi, n_sections, endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(polar=True))

        # Polished colour palette
        colors = {
            "baseline": "#e74c3c",
            "parallel": "#f39c12",
            "iterative": "#27ae60",
        }
        nice_names = {"baseline": "Baseline", "parallel": "Parallel(N=3)", "iterative": "Iterative(3R)"}

        # Collect all values first for global ring labels
        all_vals = {}
        global_max = 0
        for prefix in ["baseline", "parallel", "iterative"]:
            runs = [r for r in metrics.run_ids if r.startswith(prefix)]
            if not runs:
                continue
            avg_wc = []
            for label, _ in _REQUIRED_SECTION_GROUPS:
                vals = [metrics.section_completeness.get(r, {}).get(label, 0) for r in runs]
                avg_wc.append(sum(vals) / len(vals))
            all_vals[prefix] = avg_wc
            if avg_wc:
                global_max = max(global_max, max(avg_wc))

        if global_max == 0:
            global_max = 1

        # Draw filled polygons ? iterative on top, then parallel, then baseline
        for prefix in ["iterative", "parallel", "baseline"]:
            avg_wc = all_vals.get(prefix)
            if avg_wc is None:
                continue
            vals_norm = [v / global_max * 100 for v in avg_wc]
            vals_norm += vals_norm[:1]
            ax.fill(angles, vals_norm, alpha=0.25, color=colors[prefix],
                    edgecolor=colors[prefix], linewidth=2.2, label=nice_names[prefix])

        # ---- Axis styling ----
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(short_labels, fontsize=9, fontweight='medium')

        # Rotate and position labels outside the chart
        for label_node, angle in zip(ax.get_xticklabels(), angles[:-1]):
            deg = np.degrees(angle)
            if 90 < deg < 270:
                deg += 180
                ha = 'right'
            else:
                ha = 'left'
            label_node.set_rotation(deg)
            label_node.set_ha(ha)
            label_node.set_va('center')
            label_node.set_position((angle, 1.22))

        # Ring labels ? show actual word counts
        ring_count = 5
        ytick_vals = np.linspace(0, 100, ring_count)
        ytick_labels = [f"{int(global_max * v / 100):,}" for v in ytick_vals]
        ax.set_yticks(ytick_vals)
        ax.set_yticklabels(ytick_labels, fontsize=7, color='#888888')

        # Visible grid and rings
        ax.set_rlabel_position(30)
        ax.grid(True, color='#cccccc', linewidth=0.6, alpha=0.8)
        ax.set_facecolor('#fdfdfd')
        ax.spines['polar'].set_color('#dddddd')
        ax.spines['polar'].set_linewidth(0.8)

        # Legend
        ax.legend(loc='upper right', bbox_to_anchor=(1.32, 1.12),
                  fontsize=10, framealpha=0.92, edgecolor='#cccccc', borderpad=0.8)
        ax.set_title("Section Completeness ? Radar View", pad=32, fontsize=14, fontweight='bold')

        path = charts_dir / "section_radar.png"
        fig.savefig(path, dpi=180, bbox_inches="tight", facecolor='white')
        plt.close(fig)
        generated.append(path)
    except Exception:
        pass

    return generated


# ---- JSON export -----------------------------------------------------------

def save_metrics_json(metrics: ExperimentMetrics, output_dir: str | Path) -> Path:
    """Save all metrics as a structured JSON file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "experiment_metrics.json"
    data: dict[str, Any] = {
        "run_ids": metrics.run_ids,
        "claim_overlap_matrix": metrics.claim_overlap_matrix,
        "word_jaccard_matrix": metrics.word_jaccard_matrix,
        "section_completeness": metrics.section_completeness,
        "section_counts": metrics.section_counts,
        "costs": metrics.costs,
        "token_usage": metrics.token_usage,
        "strategy_self_consistency": {},
    }
    for prefix in ["baseline", "parallel", "iterative"]:
        cons = metrics.strategy_self_consistency(prefix)
        if cons is not None:
            data["strategy_self_consistency"][prefix] = cons
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path