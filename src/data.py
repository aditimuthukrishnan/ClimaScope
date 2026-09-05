from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd


MARKET_COLUMNS = [
    "Product Category",
    "2024 Value",
    "2025 Value",
    "2026 Value",
    "Annual Change",
    "Energy Relevance",
    "Scoring Rationale",
]

PRODUCT_COLUMNS = [
    "Portfolio Category",
    "Representative Product / Offering",
    "Product Type",
    "Primary Application",
    "Energy / Controls Relevance",
    "India Manufacturing / Presence",
    "Mapped Market Category",
    "Source Label",
    "Source URL",
]


class DataValidationError(ValueError):
    """Raised when an input file cannot safely power the dashboard."""


def _missing_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    return sorted(set(required) - set(df.columns))


def validate_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return clean market data or explain why the input cannot be used."""
    missing = _missing_columns(df, MARKET_COLUMNS)
    if missing:
        raise DataValidationError(
            "The market file is missing: " + ", ".join(missing)
        )

    clean = df.copy()
    numeric_columns = [
        "2024 Value",
        "2025 Value",
        "2026 Value",
        "Annual Change",
        "Energy Relevance",
    ]
    for column in numeric_columns:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    required_values = ["Product Category", *numeric_columns]
    empty_rows = clean[required_values].isna().any(axis=1)
    if empty_rows.any():
        row_numbers = ", ".join(str(index + 2) for index in clean.index[empty_rows])
        raise DataValidationError(
            f"Some required values are blank or invalid in row(s): {row_numbers}."
        )

    if clean["Product Category"].duplicated().any():
        duplicates = clean.loc[
            clean["Product Category"].duplicated(keep=False), "Product Category"
        ].unique()
        raise DataValidationError(
            "Each market category must appear once. Repeated: "
            + ", ".join(map(str, duplicates))
        )

    if (clean[["2024 Value", "2025 Value", "2026 Value"]] <= 0).any().any():
        raise DataValidationError("Market values must be greater than zero.")

    if not clean["Energy Relevance"].between(1, 5).all():
        raise DataValidationError(
            "The importance of energy efficiency must be scored from 1 to 5."
        )

    return clean.reset_index(drop=True)


def validate_products(df: pd.DataFrame) -> pd.DataFrame:
    missing = _missing_columns(df, PRODUCT_COLUMNS)
    if missing:
        raise DataValidationError(
            "The product file is missing: " + ", ".join(missing)
        )

    clean = df.copy()
    if clean[PRODUCT_COLUMNS].isna().any().any():
        raise DataValidationError("The product file contains blank required values.")
    return clean.reset_index(drop=True)


def load_market_csv(path: str | Path) -> pd.DataFrame:
    return validate_market_data(pd.read_csv(path))


def load_products_csv(path: str | Path) -> pd.DataFrame:
    return validate_products(pd.read_csv(path))


def read_private_workbook(source: str | Path | BinaryIO) -> pd.DataFrame:
    """Read and validate the Market Data sheet in the private Excel workbook."""
    raw = pd.read_excel(source, sheet_name="Market Data", header=3, usecols="A:M")
    raw = raw.dropna(how="all").copy()

    expected_columns = [
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
    if len(raw.columns) != len(expected_columns):
        raise DataValidationError(
            "The Market Data sheet must use the expected columns from A to M."
        )

    raw.columns = expected_columns
    market = raw[MARKET_COLUMNS].dropna(subset=["Product Category"]).copy()
    return validate_market_data(market)

