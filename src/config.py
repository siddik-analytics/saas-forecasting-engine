"""
Central configuration file for the SaaS Forecasting Engine.

Purpose:
- Keep all project paths, model assumptions, scenario settings,
  and validation thresholds in one controlled location.
- Make the forecasting model easier to maintain, audit, and scale.
"""

from dataclasses import dataclass
from pathlib import Path


# =============================================================================
# PROJECT PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DATA_DIR = DATA_DIR / "outputs"

REPORTS_DIR = BASE_DIR / "reports"
SQL_DIR = BASE_DIR / "sql"
POWERBI_DIR = BASE_DIR / "powerbi"

DUCKDB_PATH = PROCESSED_DATA_DIR / "saas_forecast.duckdb"


# =============================================================================
# MODEL TIME SETTINGS
# =============================================================================

HISTORICAL_START_DATE = "2023-01-01"
HISTORICAL_MONTHS = 36

FORECAST_START_DATE = "2026-01-01"
FORECAST_MONTHS = 36

FISCAL_YEAR_START_MONTH = 1


# =============================================================================
# SAAS SEGMENTS
# =============================================================================

CUSTOMER_SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]

REGIONS = ["North America", "EMEA", "APAC"]

PRODUCT_LINES = ["Core Platform", "Analytics Add-on", "Automation Suite"]


# =============================================================================
# BASELINE OPERATING ASSUMPTIONS
# =============================================================================

@dataclass(frozen=True)
class SaaSAssumptions:
    """
    Core SaaS business assumptions used by the forecasting engine.
    These values represent the base case unless overridden by a scenario.
    """

    # Customer movement
    logo_churn_rate: float = 0.015
    new_customer_growth_rate: float = 0.025

    # Revenue retention
    expansion_rate: float = 0.025
    contraction_rate: float = 0.0075

    # Pricing
    arpa_growth_rate: float = 0.006

    # Margins
    gross_margin: float = 0.78

    # Operating expense ratios
    sales_marketing_ratio: float = 0.34
    rnd_ratio: float = 0.24
    gna_ratio: float = 0.16

    # Sales efficiency
    cac_payback_months: int = 14

    # Cash flow
    opening_cash_balance: float = 5_000_000
    monthly_capex_ratio: float = 0.025
    working_capital_ratio: float = 0.03


BASE_ASSUMPTIONS = SaaSAssumptions()


# =============================================================================
# SCENARIO ASSUMPTIONS
# =============================================================================

SCENARIOS = {
    "base": {
        "description": "Expected operating case based on current trends.",
        "new_customer_growth_multiplier": 1.00,
        "logo_churn_multiplier": 1.00,
        "expansion_multiplier": 1.00,
        "gross_margin_adjustment": 0.00,
        "opex_multiplier": 1.00,
    },
    "upside": {
        "description": "Stronger bookings, better retention, and operating leverage.",
        "new_customer_growth_multiplier": 1.20,
        "logo_churn_multiplier": 0.85,
        "expansion_multiplier": 1.15,
        "gross_margin_adjustment": 0.02,
        "opex_multiplier": 0.96,
    },
    "downside": {
        "description": "Slower bookings, weaker retention, and margin pressure.",
        "new_customer_growth_multiplier": 0.80,
        "logo_churn_multiplier": 1.25,
        "expansion_multiplier": 0.85,
        "gross_margin_adjustment": -0.03,
        "opex_multiplier": 1.06,
    },
    "stress": {
        "description": "Severe planning case for runway and cash preservation.",
        "new_customer_growth_multiplier": 0.60,
        "logo_churn_multiplier": 1.60,
        "expansion_multiplier": 0.65,
        "gross_margin_adjustment": -0.06,
        "opex_multiplier": 1.12,
    },
}


# =============================================================================
# SEGMENT-LEVEL ASSUMPTIONS
# =============================================================================

SEGMENT_ASSUMPTIONS = {
    "SMB": {
        "starting_customers": 180,
        "starting_arpa": 450,
        "new_customer_mix": 0.55,
        "logo_churn_rate": 0.025,
        "expansion_rate": 0.015,
    },
    "Mid-Market": {
        "starting_customers": 60,
        "starting_arpa": 1_500,
        "new_customer_mix": 0.32,
        "logo_churn_rate": 0.014,
        "expansion_rate": 0.030,
    },
    "Enterprise": {
        "starting_customers": 15,
        "starting_arpa": 6_500,
        "new_customer_mix": 0.13,
        "logo_churn_rate": 0.006,
        "expansion_rate": 0.045,
    },
}


# =============================================================================
# DATA QUALITY THRESHOLDS
# =============================================================================

DATA_QUALITY_RULES = {
    "max_missing_rate": 0.01,
    "max_revenue_variance_tolerance": 0.005,
    "max_arr_mrr_reconciliation_tolerance": 0.001,
    "max_customer_rollforward_tolerance": 0,
    "allow_negative_revenue": False,
    "allow_negative_customers": False,
}


# =============================================================================
# OUTPUT FILE NAMES
# =============================================================================

RAW_OPERATING_DATA_FILE = RAW_DATA_DIR / "monthly_saas_operating_data.csv"

PROCESSED_MODEL_INPUT_FILE = PROCESSED_DATA_DIR / "model_inputs.csv"

FORECAST_OUTPUT_FILE = OUTPUT_DATA_DIR / "forecast_output.csv"
SCENARIO_OUTPUT_FILE = OUTPUT_DATA_DIR / "scenario_output.csv"
EXECUTIVE_EXCEL_OUTPUT_FILE = OUTPUT_DATA_DIR / "saas_forecast_model.xlsx"

COMMENTARY_OUTPUT_FILE = REPORTS_DIR / "executive_commentary.md"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_project_directories() -> None:
    """
    Creates required project directories if they do not already exist.
    This keeps local setup simple and prevents file-save errors.
    """

    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        OUTPUT_DATA_DIR,
        REPORTS_DIR,
        SQL_DIR,
        POWERBI_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_scenario_config(scenario_name: str) -> dict:
    """
    Returns the configuration for a selected forecast scenario.

    Args:
        scenario_name: Scenario name such as base, upside, downside, or stress.

    Returns:
        Dictionary containing scenario assumptions.

    Raises:
        ValueError: If the scenario name is not supported.
    """

    if scenario_name not in SCENARIOS:
        valid_scenarios = ", ".join(SCENARIOS.keys())
        raise ValueError(
            f"Invalid scenario '{scenario_name}'. "
            f"Valid scenarios are: {valid_scenarios}"
        )

    return SCENARIOS[scenario_name]