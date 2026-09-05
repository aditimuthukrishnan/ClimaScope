from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import DRIVER_COLUMNS


def error_metrics(actual, predicted) -> dict[str, float]:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    err = actual - predicted
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    denom = np.where(np.abs(actual) < 1e-9, np.nan, np.abs(actual))
    mape = float(np.nanmean(np.abs(err) / denom))
    return {"MAE": mae, "MAPE": mape, "RMSE": rmse}


def _category_frame(history: pd.DataFrame, drivers: pd.DataFrame, category: str) -> pd.DataFrame:
    cat = history.loc[history["Product Category"] == category, ["Year", "Demand Index"]].copy()
    cat = cat.sort_values("Year")
    merged = cat.merge(drivers, on="Year", how="left")
    merged["Demand Growth"] = merged["Demand Index"].pct_change()
    return merged


def recent_cagr(values: pd.Series, lookback_periods: int = 4) -> float:
    values = pd.Series(values, dtype=float).dropna().reset_index(drop=True)
    if len(values) < 2:
        return 0.0
    periods = min(lookback_periods, len(values) - 1)
    start = values.iloc[-periods - 1]
    end = values.iloc[-1]
    if start <= 0 or end <= 0:
        return float(values.pct_change().dropna().tail(periods).mean())
    return float((end / start) ** (1 / periods) - 1)


def _fit_driver_model(train: pd.DataFrame) -> Pipeline:
    model_rows = train.dropna(subset=["Demand Growth", *DRIVER_COLUMNS])
    if len(model_rows) < 5:
        raise ValueError("At least five growth observations are required for the driver model.")
    model = Pipeline([
        ("scale", StandardScaler()),
        ("ridge", Ridge(alpha=2.0)),
    ])
    model.fit(model_rows[DRIVER_COLUMNS], model_rows["Demand Growth"])
    return model


def _recursive_forecast(last_value: float, growth_rates) -> np.ndarray:
    out = []
    value = float(last_value)
    for rate in growth_rates:
        rate = float(np.clip(rate, -0.12, 0.30))
        value *= 1 + rate
        out.append(value)
    return np.asarray(out)


def backtest_category(
    history: pd.DataFrame,
    drivers: pd.DataFrame,
    category: str,
    validation_years: int = 3,
) -> dict:
    frame = _category_frame(history, drivers, category)
    if len(frame) <= validation_years + 4:
        raise ValueError(f"Not enough history to backtest {category}.")

    cutoff = int(frame["Year"].max() - validation_years)
    train = frame[frame["Year"] <= cutoff].copy()
    valid = frame[frame["Year"] > cutoff].copy()

    baseline_rate = recent_cagr(train["Demand Index"], lookback_periods=4)
    baseline_pred = _recursive_forecast(train["Demand Index"].iloc[-1], [baseline_rate] * len(valid))

    driver_model = _fit_driver_model(train)
    driver_growth = driver_model.predict(valid[DRIVER_COLUMNS])
    driver_pred = _recursive_forecast(train["Demand Index"].iloc[-1], driver_growth)

    actual = valid["Demand Index"].to_numpy(dtype=float)
    baseline_metrics = error_metrics(actual, baseline_pred)
    driver_metrics = error_metrics(actual, driver_pred)

    # Prefer the simpler baseline when its MAPE is effectively tied (within 0.5 percentage points).
    if driver_metrics["MAPE"] + 0.005 < baseline_metrics["MAPE"]:
        winner = "Driver-based"
    else:
        winner = "Baseline"

    validation = pd.DataFrame({
        "Year": valid["Year"].astype(int).to_numpy(),
        "Actual": actual,
        "Baseline": baseline_pred,
        "Driver-based": driver_pred,
    })

    return {
        "Product Category": category,
        "Winner": winner,
        "Baseline MAE": baseline_metrics["MAE"],
        "Baseline MAPE": baseline_metrics["MAPE"],
        "Baseline RMSE": baseline_metrics["RMSE"],
        "Driver MAE": driver_metrics["MAE"],
        "Driver MAPE": driver_metrics["MAPE"],
        "Driver RMSE": driver_metrics["RMSE"],
        "Validation": validation,
    }


def forecast_category(
    history: pd.DataFrame,
    drivers: pd.DataFrame,
    future_drivers: pd.DataFrame,
    category: str,
    model_name: str | None = None,
) -> tuple[pd.DataFrame, dict]:
    frame = _category_frame(history, drivers, category)
    diagnostic = backtest_category(history, drivers, category)
    selected = model_name or diagnostic["Winner"]

    future = future_drivers.sort_values("Year").copy()
    last_value = float(frame["Demand Index"].iloc[-1])

    if selected == "Baseline":
        rate = recent_cagr(frame["Demand Index"], lookback_periods=4)
        growth = np.repeat(rate, len(future))
    elif selected == "Driver-based":
        model = _fit_driver_model(frame)
        growth = model.predict(future[DRIVER_COLUMNS])
    else:
        raise ValueError("model_name must be 'Baseline', 'Driver-based', or None.")

    values = _recursive_forecast(last_value, growth)
    result = pd.DataFrame({
        "Product Category": category,
        "Year": future["Year"].astype(int).to_numpy(),
        "Forecast Demand": values,
        "Forecast Growth": np.clip(growth, -0.12, 0.30),
        "Model": selected,
    })
    return result, diagnostic


def forecast_all(
    history: pd.DataFrame,
    drivers: pd.DataFrame,
    future_drivers: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    forecasts = []
    diagnostics = []
    for category in sorted(history["Product Category"].unique()):
        fc, diag = forecast_category(history, drivers, future_drivers, category)
        forecasts.append(fc)
        diagnostics.append({k: v for k, v in diag.items() if k != "Validation"})
    return pd.concat(forecasts, ignore_index=True), pd.DataFrame(diagnostics)
