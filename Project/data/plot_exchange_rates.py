from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).resolve().parent

RATES_FILE = (
    DATA_DIR
    / "cleaning_output"
    / "fx_eur_8currencies_2010_2025.csv"
)

RETURNS_FILE = (
    DATA_DIR
    / "analysis_output"
    / "fx_daily_log_returns_2010_2025.csv"
)

FIGURE_DIR = DATA_DIR / "analysis_output" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

CURRENCIES = [
    "CNY", "USD", "JPY", "GBP",
    "HKD", "CHF", "AUD", "CAD"
]

# Read and sort both datasets.
rates = pd.read_csv(RATES_FILE, parse_dates=["Date"])
returns = pd.read_csv(RETURNS_FILE, parse_dates=["Date"])

rates = rates.sort_values("Date").set_index("Date")
returns = returns.sort_values("Date").set_index("Date")

# Set the first exchange rate of each currency to 100.
indexed_rates = (
    rates[CURRENCIES]
    .div(rates[CURRENCIES].iloc[0])
    * 100
)

# Figure 1: Indexed exchange rates.
fig, ax = plt.subplots(figsize=(13, 7))

for currency in CURRENCIES:
    ax.plot(
        indexed_rates.index,
        indexed_rates[currency],
        label=currency,
        linewidth=1.2
    )

ax.axhline(100, color="gray", linestyle="--", linewidth=1)
ax.set_title("Exchange Rates Against EUR: First Observation = 100")
ax.set_xlabel("Date")
ax.set_ylabel("Exchange Rate Index")
ax.legend(ncol=4)
ax.grid(alpha=0.25)

fig.tight_layout()
fig.savefig(
    FIGURE_DIR / "indexed_exchange_rates.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close(fig)

# Figure 2: Daily log changes, expressed as percentages.
# Use the same vertical scale to make volatility comparable.
fig, axes = plt.subplots(
    4, 2,
    figsize=(14, 12),
    sharex=True,
    sharey=True
)

for ax, currency in zip(axes.flat, CURRENCIES):
    ax.plot(
        returns.index,
        returns[currency] * 100,
        linewidth=0.6
    )
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_title(currency)
    ax.set_ylabel("Daily log change (%)")
    ax.grid(alpha=0.25)

for ax in axes[-1]:
    ax.set_xlabel("Date")

fig.suptitle(
    "Daily Log Changes in Foreign Currency Units per EUR",
    fontsize=15
)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(
    FIGURE_DIR / "daily_log_returns.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close(fig)

print("Figures saved to:", FIGURE_DIR)
print("1. indexed_exchange_rates.png")
print("2. daily_log_returns.png")