from functools import lru_cache
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from .config import (
    CAPABILITY_FILE,
    DRIVER_HISTORY_FILE,
    FINANCIAL_FILE,
    HISTORY_FILE,
    MARKET_FILE,
    PRODUCTS_FILE,
    SCENARIO_FILE,
    SUPPLY_FILE,
)


@lru_cache(maxsize=1)
def load_demo_bundle() -> dict[str, pd.DataFrame]:
    """Load the public, illustrative demo bundle used by the deployed app."""
    return {
        "market": pd.read_csv(MARKET_FILE),
        "history": pd.read_csv(HISTORY_FILE),
        "drivers": pd.read_csv(DRIVER_HISTORY_FILE),
        "scenarios": pd.read_csv(SCENARIO_FILE),
        "capability": pd.read_csv(CAPABILITY_FILE),
        "supply": pd.read_csv(SUPPLY_FILE),
        "financial": pd.read_csv(FINANCIAL_FILE),
        "products": pd.read_csv(PRODUCTS_FILE),
    }


def read_private_market_workbook(source: str | Path | BinaryIO) -> pd.DataFrame:
    """Compatibility reader for the original private BSRIA market workbook."""
    raw = pd.read_excel(source, sheet_name="Market Data", header=3, usecols="A:M")
    raw = raw.iloc[:6].copy()
    raw.columns = [
        "Product Category",
        "2024 Value",
        "2025 Value",
        "2026 Value",
        "Annual Change",
        "Absolute Growth",
        "2026 Market Share",
        "Market Size Score",
        "Growth Score",
        "Energy Relevance",
        "Opportunity Score",
        "Priority Rank",
        "Scoring Rationale",
    ]
    numeric_cols = [
        "2024 Value", "2025 Value", "2026 Value", "Annual Change", "Absolute Growth",
        "2026 Market Share", "Market Size Score", "Growth Score", "Energy Relevance",
        "Opportunity Score", "Priority Rank",
    ]
    for col in numeric_cols:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    return raw.dropna(subset=["Product Category", "2026 Value"]).reset_index(drop=True)
