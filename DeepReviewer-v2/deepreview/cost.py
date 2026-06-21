# cost.py -- Token-to-cost conversion and per-phase expense tracking.
#
# Usage:
#   from deepreview.cost import CostTracker, load_pricing
#
#   tracker = CostTracker(pricing=load_pricing())
#   tracker.record_phase("mineru_parse", model="mineru-vlm", fixed_cost=0.02)
#   tracker.record_phase("agent_run", model="deepseek-v4-pro", input_tokens=45230, output_tokens=12450)
#   print(tracker.format_table())

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---- Pricing data model ----------------------------------------------------

@dataclass
class TokenPricing:
    """Price per 1M tokens for a specific model/provider."""
    model: str
    provider: str = ""
    input_price_per_1m: float = 0.0
    output_price_per_1m: float = 0.0
    cached_input_price_per_1m: float = 0.0
    notes: str = ""


# ---- Per-phase cost record -------------------------------------------------

@dataclass
class PhaseCost:
    """Cost breakdown for a single pipeline phase."""
    phase: str
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    input_cost: float = 0.0
    output_cost: float = 0.0
    cached_cost: float = 0.0
    fixed_cost: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def total_cost(self) -> float:
        return self.input_cost + self.output_cost + self.cached_cost + self.fixed_cost


# ---- Cost summary ----------------------------------------------------------

@dataclass
class CostSummary:
    phases: list[PhaseCost] = field(default_factory=list)
    extra_notes: list[str] = field(default_factory=list)

    @property
    def total_input_tokens(self) -> int:
        return sum(p.input_tokens for p in self.phases)

    @property
    def total_output_tokens(self) -> int:
        return sum(p.output_tokens for p in self.phases)

    @property
    def total_cost(self) -> float:
        return sum(p.total_cost for p in self.phases)

    def to_dict(self) -> dict:
        return {
            "phases": [
                {
                    "phase": p.phase,
                    "model": p.model,
                    "input_tokens": p.input_tokens,
                    "output_tokens": p.output_tokens,
                    "cached_tokens": p.cached_tokens,
                    "input_cost": round(p.input_cost, 6),
                    "output_cost": round(p.output_cost, 6),
                    "cached_cost": round(p.cached_cost, 6),
                    "fixed_cost": round(p.fixed_cost, 6),
                    "total_cost": round(p.total_cost, 6),
                }
                for p in self.phases
            ],
            "totals": {
                "input_tokens": self.total_input_tokens,
                "output_tokens": self.total_output_tokens,
                "total_cost": round(self.total_cost, 6),
            },
            "extra_notes": self.extra_notes,
        }


# ---- Cost tracker ----------------------------------------------------------

class CostTracker:
    """Accumulates per-phase costs throughout a review pipeline run."""

    def __init__(self, pricing: dict[str, TokenPricing] | None = None, *, currency: str = "¥"):
        self.pricing = pricing or {}
        self.phases: list[PhaseCost] = []
        self.currency = currency

    def _lookup(self, model: str) -> TokenPricing | None:
        if not model:
            return None
        key = model.strip().lower()
        if key in self.pricing:
            return self.pricing[key]
        for k, v in self.pricing.items():
            if key.startswith(k) or k.startswith(key):
                return v
        return None

    def record_phase(
        self,
        phase: str,
        *,
        model: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
        cached_tokens: int = 0,
        fixed_cost: float = 0.0,
    ) -> PhaseCost:
        pricing = self._lookup(model)
        pc = PhaseCost(
            phase=phase,
            model=model or (pricing.model if pricing else "unknown"),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            fixed_cost=fixed_cost,
        )
        if pricing:
            pc.input_cost = (input_tokens / 1_000_000) * pricing.input_price_per_1m
            pc.output_cost = (output_tokens / 1_000_000) * pricing.output_price_per_1m
            pc.cached_cost = (cached_tokens / 1_000_000) * pricing.cached_input_price_per_1m
        self.phases.append(pc)
        return pc

    def record_from_token_usage(
        self, phase: str, *, model: str, token_usage: dict[str, int],
    ) -> PhaseCost:
        return self.record_phase(
            phase=phase,
            model=model,
            input_tokens=int(token_usage.get("input_tokens", 0)),
            output_tokens=int(token_usage.get("output_tokens", 0)),
        )

    def summary(self) -> CostSummary:
        return CostSummary(phases=list(self.phases))

    # ---- Formatting --------------------------------------------------------

    def format_table(self, title: str = "Cost Breakdown") -> str:
        if not self.phases:
            return f"## {title}\n\n*No cost data recorded.*\n"
        c = self.currency
        lines = [
            f"## {title}",
            "",
            f"| Phase | Model | Input Tokens | Output Tokens | Cost ({c}) |",
            "|-------|-------|-------------|---------------|------------|",
        ]
        for p in self.phases:
            lines.append(
                f"| {p.phase} | {p.model} | {p.input_tokens:,} | {p.output_tokens:,} | "
                f"{c}{p.total_cost:.4f} |"
            )
        s = self.summary()
        lines.append("")
        lines.append(
            f"**TOTAL:** {s.total_input_tokens:,} input + "
            f"{s.total_output_tokens:,} output tokens, "
            f"**{c}{s.total_cost:.4f}**"
        )
        return "\n".join(lines)

    def format_csv(self) -> str:
        rows = ["phase,model,input_tokens,output_tokens,input_cost,output_cost,fixed_cost,total_cost"]
        for p in self.phases:
            rows.append(
                f"{p.phase},{p.model},{p.input_tokens},{p.output_tokens},"
                f"{p.input_cost:.6f},{p.output_cost:.6f},{p.fixed_cost:.6f},{p.total_cost:.6f}"
            )
        return "\n".join(rows)

    # ---- Persistence -------------------------------------------------------

    def to_dict(self) -> dict:
        return self.summary().to_dict()

    def save_json(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def save_markdown(self, path: str | Path, title: str = "Cost Breakdown") -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.format_table(title), encoding="utf-8")


# ---- Preset pricing --------------------------------------------------------
# DeepSeek V4: CNY. Other models: USD as publicly listed.

PRESET_PRICING: dict[str, TokenPricing] = {
    # DeepSeek V4 series (CNY)
    "deepseek-v4-flash": TokenPricing(
        model="deepseek-v4-flash",
        provider="DeepSeek",
        input_price_per_1m=1.0,
        output_price_per_1m=2.0,
        cached_input_price_per_1m=0.02,
        notes="DeepSeek-V4-Flash. CNY: 1/0.02/2 (input cache-miss/hit / output) per 1M tokens.",
    ),
    "deepseek-v4-pro": TokenPricing(
        model="deepseek-v4-pro",
        provider="DeepSeek",
        input_price_per_1m=3.0,
        output_price_per_1m=6.0,
        cached_input_price_per_1m=0.025,
        notes="DeepSeek-V4-Pro. CNY: 3/0.025/6 per 1M tokens.",
    ),
    # DeepSeek legacy (USD)
    "deepseek-chat": TokenPricing(
        model="deepseek-chat", provider="DeepSeek",
        input_price_per_1m=0.27, output_price_per_1m=1.10,
    ),
    "deepseek-v3": TokenPricing(
        model="deepseek-v3", provider="DeepSeek",
        input_price_per_1m=0.27, output_price_per_1m=1.10,
    ),
    "deepseek-reasoner": TokenPricing(
        model="deepseek-reasoner", provider="DeepSeek",
        input_price_per_1m=0.55, output_price_per_1m=2.19,
    ),
    "deepseek-r1": TokenPricing(
        model="deepseek-r1", provider="DeepSeek",
        input_price_per_1m=0.55, output_price_per_1m=2.19,
    ),
    # OpenAI (USD)
    "gpt-4o": TokenPricing(
        model="gpt-4o", provider="OpenAI",
        input_price_per_1m=2.50, output_price_per_1m=10.00, cached_input_price_per_1m=1.25,
    ),
    "gpt-4o-mini": TokenPricing(
        model="gpt-4o-mini", provider="OpenAI",
        input_price_per_1m=0.15, output_price_per_1m=0.60, cached_input_price_per_1m=0.075,
    ),
    "gpt-5.2": TokenPricing(
        model="gpt-5.2", provider="OpenAI",
        input_price_per_1m=1.75, output_price_per_1m=14.00,
        notes="Placeholder -- update with actual GPT-5.2 rates.",
    ),
    "gpt-5.4": TokenPricing(
        model="gpt-5.4", provider="OpenAI",
        input_price_per_1m=1.75, output_price_per_1m=14.00,
        notes="Placeholder.",
    ),
    # Anthropic (USD)
    "claude-sonnet-4-20250514": TokenPricing(
        model="claude-sonnet-4-20250514", provider="Anthropic",
        input_price_per_1m=3.00, output_price_per_1m=15.00, cached_input_price_per_1m=0.30,
    ),
    "claude-3.5-sonnet": TokenPricing(
        model="claude-3.5-sonnet", provider="Anthropic",
        input_price_per_1m=3.00, output_price_per_1m=15.00,
    ),
}


# ---- Pricing loader --------------------------------------------------------

def load_pricing(
    config_path: str | Path | None = None,
    *,
    include_presets: bool = True,
) -> dict[str, TokenPricing]:
    """Load pricing from JSON config, merged with presets.

    Config JSON format:
    {"models": {"model-name": {"input_price_per_1m": 1.0, ...}}}
    """
    pricing: dict[str, TokenPricing] = {}
    if include_presets:
        pricing.update(PRESET_PRICING)
    if config_path:
        path = Path(config_path)
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            models: dict = raw.get("models", raw) if isinstance(raw, dict) else {}
            for key, entry in models.items():
                if isinstance(entry, dict):
                    pricing[key.strip().lower()] = TokenPricing(
                        model=str(entry.get("model", key)),
                        provider=str(entry.get("provider", "")),
                        input_price_per_1m=float(entry.get("input_price_per_1m", 0)),
                        output_price_per_1m=float(entry.get("output_price_per_1m", 0)),
                        cached_input_price_per_1m=float(entry.get("cached_input_price_per_1m", 0)),
                        notes=str(entry.get("notes", "")),
                    )
    return pricing


def merge_tracker_from_runs(
    tracker: CostTracker,
    *,
    phase_prefix: str,
    run_results: list[Any],
    model: str,
) -> None:
    """Add per-run sub-phases from a list of ReviewRunResult objects."""
    for rr in run_results:
        idx = getattr(rr, "run_index", 0)
        tracker.record_from_token_usage(
            phase=f"{phase_prefix}_run_{idx + 1}",
            model=model,
            token_usage=getattr(rr, "token_usage", {}),
        )