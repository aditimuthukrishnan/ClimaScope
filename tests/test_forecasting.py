import numpy as np

from src.data_loader import load_demo_bundle
from src.forecasting import backtest_category, error_metrics, forecast_category


def test_error_metrics_are_correct():
    m = error_metrics([100, 120], [90, 126])
    assert np.isclose(m["MAE"], 8.0)
    assert m["MAPE"] > 0
    assert m["RMSE"] > 0


def test_backtest_returns_supported_winner():
    bundle = load_demo_bundle()
    diag = backtest_category(bundle["history"], bundle["drivers"], "Chillers")
    assert diag["Winner"] in {"Baseline", "Driver-based"}
    assert diag["Baseline MAPE"] >= 0
    assert diag["Driver MAPE"] >= 0


def test_forecasts_are_positive_and_complete():
    bundle = load_demo_bundle()
    future = bundle["scenarios"].query("Scenario == 'Base'")
    fc, _ = forecast_category(bundle["history"], bundle["drivers"], future, "AHUs & FCUs")
    assert len(fc) == 5
    assert (fc["Forecast Demand"] > 0).all()
    assert fc["Year"].tolist() == [2027, 2028, 2029, 2030, 2031]
