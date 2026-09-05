from __future__ import annotations

import numpy as np
import pandas as pd

from .config import CAPABILITY_WEIGHTS, MARKET_WEIGHTS, STRATEGY_WEIGHTS, SUPPLY_WEIGHTS


def minmax_score(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").fillna(0.0)
    spread = float(s.max() - s.min())
    if spread <= 1e-12:
        return pd.Series(np.full(len(s), 3.0), index=s.index)
    return 1.0 + 4.0 * (s - s.min()) / spread


def _weighted_average(df: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    total = sum(weights.values()) or 1.0
    result = pd.Series(0.0, index=df.index)
    for col, weight in weights.items():
        result = result + pd.to_numeric(df[col], errors="coerce").fillna(3.0) * weight
    return result / total


def market_attractiveness(
    forecast_summary: pd.DataFrame,
    market: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    weights = weights or MARKET_WEIGHTS
    out = forecast_summary.merge(
        market[["Product Category", "Energy Relevance", "Scoring Rationale"]],
        on="Product Category",
        how="left",
    )
    out["Market Size Score"] = minmax_score(out["Forecast Demand"])
    out["Growth Score"] = minmax_score(out["Forecast CAGR"])
    out["Energy Relevance"] = pd.to_numeric(out["Energy Relevance"], errors="coerce").fillna(3.0)
    total = sum(weights.values()) or 1.0
    out["Market Attractiveness"] = (
        out["Market Size Score"] * weights["size"]
        + out["Growth Score"] * weights["growth"]
        + out["Energy Relevance"] * weights["energy"]
    ) / total
    return out


def capability_fit(capability: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.DataFrame:
    weights = weights or CAPABILITY_WEIGHTS
    out = capability.copy()
    out["Carrier Capability Fit"] = _weighted_average(out, weights)
    return out


def supply_readiness(supply: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.DataFrame:
    weights = weights or SUPPLY_WEIGHTS
    out = supply.copy()
    # Import dependency and lead-time risk are adverse, so invert the 1-5 scale.
    transformed = out.copy()
    transformed["Import Dependency"] = 6 - transformed["Import Dependency"]
    transformed["Lead-Time Risk"] = 6 - transformed["Lead-Time Risk"]
    out["Supply Readiness"] = _weighted_average(transformed, weights)
    return out


def financial_and_capacity(
    forecast_summary: pd.DataFrame,
    history: pd.DataFrame,
    financial: pd.DataFrame,
    target_share_override: float | None = None,
) -> pd.DataFrame:
    latest = (
        history.sort_values("Year")
        .groupby("Product Category", as_index=False)
        .tail(1)[["Product Category", "Demand Index"]]
        .rename(columns={"Demand Index": "2026 Demand"})
    )
    out = forecast_summary.merge(financial, on="Product Category", how="left").merge(latest, on="Product Category", how="left")
    if target_share_override is not None:
        out["Applied Target Share"] = float(target_share_override)
    else:
        out["Applied Target Share"] = out["Target Share"]

    ratio = out["Forecast Demand"] / out["2026 Demand"]
    out["Forecast Market Value (₹ cr, illustrative)"] = out["2026 Market Value (₹ cr, illustrative)"] * ratio
    out["Revenue Potential (₹ cr, illustrative)"] = out["Forecast Market Value (₹ cr, illustrative)"] * out["Applied Target Share"]
    out["Profit Potential (₹ cr, illustrative)"] = out["Revenue Potential (₹ cr, illustrative)"] * out["Operating Margin"]
    out["Simple ROI"] = out["Profit Potential (₹ cr, illustrative)"] / out["Required Investment (₹ cr, illustrative)"].replace(0, np.nan)
    out["Payback (years)"] = out["Required Investment (₹ cr, illustrative)"] / out["Profit Potential (₹ cr, illustrative)"].replace(0, np.nan)
    out["Required Capacity (index-share units)"] = out["Forecast Demand"] * out["Applied Target Share"]
    out["Capacity Gap (index-share units)"] = out["Required Capacity (index-share units)"] - out["Current Capacity (index-share units)"]

    profit_score = minmax_score(out["Profit Potential (₹ cr, illustrative)"])
    roi_score = minmax_score(out["Simple ROI"].replace([np.inf, -np.inf], np.nan).fillna(0.0))
    out["Financial Attractiveness"] = 0.60 * profit_score + 0.40 * roi_score
    return out


def recommendation_for_row(row: pd.Series) -> str:
    market = float(row["Market Attractiveness"])
    capability = float(row["Carrier Capability Fit"])
    supply = float(row["Supply Readiness"])
    financial = float(row["Financial Attractiveness"])
    localisation = float(row["Localisation Level"])

    if market < 2.45 and financial < 2.8:
        return "Deprioritise"
    if market >= 3.40 and supply < 3.25 and localisation < 3.25:
        return "Localise First"
    if market >= 3.55 and capability < 3.75:
        return "Build Capability"
    if market >= 4.05 and capability >= 4.25 and supply >= 3.55 and financial >= 3.55:
        return "Invest"
    if market >= 3.45 and capability >= 3.75 and supply >= 3.20:
        return "Scale"
    return "Monitor"


def combine_strategy(
    market_scores: pd.DataFrame,
    capability_scores: pd.DataFrame,
    supply_scores: pd.DataFrame,
    finance_scores: pd.DataFrame,
) -> pd.DataFrame:
    out = market_scores.merge(
        capability_scores,
        on="Product Category",
        how="left",
        suffixes=("", "_cap"),
    ).merge(
        supply_scores,
        on="Product Category",
        how="left",
        suffixes=("", "_supply"),
    ).merge(
        finance_scores,
        on=["Product Category", "Forecast Demand", "Forecast CAGR", "Model"],
        how="left",
        suffixes=("", "_fin"),
    )

    w = STRATEGY_WEIGHTS
    out["Strategic Score"] = (
        out["Market Attractiveness"] * w["Market Attractiveness"]
        + out["Carrier Capability Fit"] * w["Carrier Capability Fit"]
        + out["Supply Readiness"] * w["Supply Readiness"]
        + out["Financial Attractiveness"] * w["Financial Attractiveness"]
    ) / sum(w.values())
    out["Recommendation"] = out.apply(recommendation_for_row, axis=1)
    out["Priority Rank"] = out["Strategic Score"].rank(method="dense", ascending=False).astype(int)
    return out.sort_values(["Priority Rank", "Product Category"]).reset_index(drop=True)
