from __future__ import annotations

import numpy as np
import pandas as pd


DEFAULT_WEIGHTS = {
    "market_size": 0.40,
    "growth": 0.35,
    "energy": 0.25,
}


def minmax_score(series: pd.Series) -> pd.Series:
    """Place a set of values on a comparable 1-to-5 scale."""
    values = pd.to_numeric(series, errors="coerce").fillna(0.0)
    spread = values.max() - values.min()
    if spread == 0:
        return pd.Series(np.full(len(values), 3.0), index=values.index)
    return 1.0 + 4.0 * (values - values.min()) / spread


def calculate_scores(
    df: pd.DataFrame,
    size_weight: float = DEFAULT_WEIGHTS["market_size"],
    growth_weight: float = DEFAULT_WEIGHTS["growth"],
    energy_weight: float = DEFAULT_WEIGHTS["energy"],
) -> pd.DataFrame:
    """Rank categories and retain each part of the score for explanation."""
    out = df.copy()
    out["Market Size Score"] = minmax_score(out["2026 Value"])
    out["Growth Score"] = minmax_score(out["Annual Change"])
    out["Energy Relevance"] = pd.to_numeric(
        out["Energy Relevance"], errors="coerce"
    ).fillna(3.0)

    weight_sum = size_weight + growth_weight + energy_weight
    if weight_sum <= 0:
        size_weight = DEFAULT_WEIGHTS["market_size"]
        growth_weight = DEFAULT_WEIGHTS["growth"]
        energy_weight = DEFAULT_WEIGHTS["energy"]
        weight_sum = 1.0

    normalised_size = size_weight / weight_sum
    normalised_growth = growth_weight / weight_sum
    normalised_energy = energy_weight / weight_sum

    out["Market size contribution"] = out["Market Size Score"] * normalised_size
    out["Growth contribution"] = out["Growth Score"] * normalised_growth
    out["Energy contribution"] = out["Energy Relevance"] * normalised_energy
    out["Opportunity Score"] = out[
        [
            "Market size contribution",
            "Growth contribution",
            "Energy contribution",
        ]
    ].sum(axis=1)
    out["Priority Rank"] = (
        out["Opportunity Score"].rank(method="dense", ascending=False).astype(int)
    )
    return out.sort_values(
        ["Priority Rank", "Product Category"]
    ).reset_index(drop=True)


def category_action(row: pd.Series) -> str:
    """Translate the scores into a short leadership action."""
    if row["Priority Rank"] == 1:
        return "Build the business case and test whether supply can support growth."
    if row["Opportunity Score"] >= 3.5:
        return "Keep in the near-term growth plan and close the main product gaps."
    if row["Annual Change"] >= 0.10:
        return "Track demand closely and validate where Carrier can compete profitably."
    return "Protect the current position and invest only where returns are clear."

