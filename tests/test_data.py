from __future__ import annotations

import pandas as pd
import unittest

from src.data import DataValidationError, validate_market_data


def valid_market_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Product Category": ["Chillers", "VRF Systems"],
            "2024 Value": [100, 100],
            "2025 Value": [110, 108],
            "2026 Value": [120, 118],
            "Annual Change": [0.10, 0.09],
            "Energy Relevance": [5, 4],
            "Scoring Rationale": ["Large buildings", "Flexible zoning"],
        }
    )


class MarketDataTests(unittest.TestCase):
    def test_market_data_accepts_valid_rows(self) -> None:
        result = validate_market_data(valid_market_data())
        self.assertEqual(len(result), 2)

    def test_market_data_rejects_repeated_categories(self) -> None:
        data = valid_market_data()
        data.loc[1, "Product Category"] = "Chillers"

        with self.assertRaisesRegex(DataValidationError, "Each market category"):
            validate_market_data(data)

    def test_market_data_rejects_energy_rating_outside_scale(self) -> None:
        data = valid_market_data()
        data.loc[0, "Energy Relevance"] = 6

        with self.assertRaisesRegex(DataValidationError, "scored from 1 to 5"):
            validate_market_data(data)
