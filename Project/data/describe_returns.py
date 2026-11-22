from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    DATA_DIR
    / "analysis_output"
    / "fx_daily_log_returns_2010_2025.csv"
)

OUTPUT_FILE = (
    DATA_DIR
    / "analysis_output"
    / "daily_returns_summary.csv"
)

CURRENCIES = [
    "CNY", "USD", "JPY", "GBP",
    "HKD", "CHF", "AUD", "CAD"
]

# Read the daily log returns.
df = pd.read_csv(INPUT_FILE)

# Calculate statistics for each currency.
summary = df[CURRENCIES].agg(
    ["count", "mean", "median", "std", "min", "max"]
).T

# Express return statistics as percentages.
PERCENT_COLUMNS = ["mean", "median", "std", "min", "max"]
summary[PERCENT_COLUMNS] = summary[PERCENT_COLUMNS] * 100

# Give the output columns clear names.
summary = summary.rename(columns={
    "count": "observations",
    "mean": "mean_daily_return_pct",
    "median": "median_daily_return_pct",
    "std": "daily_volatility_pct",
    "min": "minimum_daily_return_pct",
    "max": "maximum_daily_return_pct"
})

summary.index.name = "currency"

# Save and display the result.
summary.to_csv(OUTPUT_FILE, float_format="%.6f")

print(summary.round(4))
print("\nSaved to:", OUTPUT_FILE)