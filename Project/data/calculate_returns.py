from pathlib import Path
import numpy as np
import pandas as pd

# Locate the cleaned data relative to this script.
DATA_DIR = Path(__file__).resolve().parent
INPUT_FILE = (
    DATA_DIR
    / "cleaning_output"
    / "fx_eur_8currencies_2010_2025.csv"
)

OUTPUT_DIR = DATA_DIR / "analysis_output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "fx_daily_log_returns_2010_2025.csv"

CURRENCIES = [
    "CNY", "USD", "JPY", "GBP",
    "HKD", "CHF", "AUD", "CAD"
]

# Read the cleaned exchange rates.
df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])

# Check that the input has the expected structure.
assert df.columns.tolist() == ["Date"] + CURRENCIES
assert df["Date"].is_monotonic_increasing
assert df["Date"].is_unique
assert df[CURRENCIES].notna().all().all()
assert (df[CURRENCIES] > 0).all().all()

# Keep the date corresponding to each calculated change.
returns = df[["Date"]].copy()

# Daily log return = ln(today's rate / previous observation's rate).
for currency in CURRENCIES:
    returns[currency] = np.log(
        df[currency] / df[currency].shift(1)
    )

# The first observation has no previous rate, so remove that row.
returns = returns.dropna().reset_index(drop=True)

# Check the result before saving.
assert len(returns) == len(df) - 1
assert returns[CURRENCIES].notna().all().all()

returns.to_csv(
    OUTPUT_FILE,
    index=False,
    date_format="%Y-%m-%d"
)

print("Input rows:", len(df))
print("Output rows:", len(returns))
print("First return date:", returns["Date"].iloc[0].date())
print("Last return date:", returns["Date"].iloc[-1].date())
print("Saved to:", OUTPUT_FILE)
print(returns.head())