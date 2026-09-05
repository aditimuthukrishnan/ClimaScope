from __future__ import annotations

import pandas as pd
import unittest

from src.scoring import calculate_scores, minmax_score


def sample_scores() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Product Category": ["A", "B"],
            "2026 Value": [100, 200],
            "Annual Change": [0.05, 0.15],
            "Energy Relevance": [3, 5],
        }
    )


class ScoringTests(unittest.TestCase):
    def test_equal_values_receive_middle_rating(self) -> None:
        result = minmax_score(pd.Series([10, 10, 10]))
        self.assertEqual(result.tolist(), [3.0, 3.0, 3.0])

    def test_score_parts_add_to_total(self) -> None:
        result = calculate_scores(sample_scores())
        parts = result[
            [
                "Market size contribution",
                "Growth contribution",
                "Energy contribution",
            ]
        ].sum(axis=1)

        self.assertTrue(
            parts.round(8).equals(result["Opportunity Score"].round(8))
        )
        self.assertEqual(result.iloc[0]["Product Category"], "B")

    def test_zero_weights_use_standard_mix(self) -> None:
        result = calculate_scores(sample_scores(), 0, 0, 0)
        self.assertTrue(result["Opportunity Score"].notna().all())
