from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PRIVATE_DIR = ROOT / "private_input"

MARKET_FILE = DATA_DIR / "market_demo.csv"
HISTORY_FILE = DATA_DIR / "forecast_history_demo.csv"
DRIVER_HISTORY_FILE = DATA_DIR / "driver_history_demo.csv"
SCENARIO_FILE = DATA_DIR / "scenario_drivers_demo.csv"
CAPABILITY_FILE = DATA_DIR / "capability_scores_demo.csv"
SUPPLY_FILE = DATA_DIR / "supply_readiness_demo.csv"
FINANCIAL_FILE = DATA_DIR / "financial_inputs_demo.csv"
PRODUCTS_FILE = DATA_DIR / "carrier_products_public.csv"

DRIVER_COLUMNS = [
    "Economic Activity Growth",
    "Construction Growth",
    "Data Centre Growth",
    "Urbanisation Growth",
    "Electricity Growth",
]

MARKET_WEIGHTS = {"size": 0.40, "growth": 0.35, "energy": 0.25}
CAPABILITY_WEIGHTS = {
    "Product Coverage": 0.25,
    "Technology Fit": 0.25,
    "Competitive Position": 0.20,
    "Service Capability": 0.15,
    "Distribution Capability": 0.15,
}
SUPPLY_WEIGHTS = {
    "Localisation Level": 0.30,
    "Supplier Availability": 0.25,
    "Import Dependency": 0.25,
    "Lead-Time Risk": 0.20,
}
STRATEGY_WEIGHTS = {
    "Market Attractiveness": 0.35,
    "Carrier Capability Fit": 0.30,
    "Supply Readiness": 0.15,
    "Financial Attractiveness": 0.20,
}

ACTIONS = ["Invest", "Scale", "Build Capability", "Localise First", "Monitor", "Deprioritise"]
