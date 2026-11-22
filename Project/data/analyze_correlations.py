from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = DATA_DIR / "analysis_output"
FIGURE_DIR = OUTPUT_DIR / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = OUTPUT_DIR / "fx_daily_log_returns_2010_2025.csv"

CURRENCIES = [
    "CNY", "USD", "JPY", "GBP",
    "HKD", "CHF", "AUD", "CAD"
]

# Read the daily log changes.
df = pd.read_csv(INPUT_FILE)
values = df[CURRENCIES].apply(pd.to_numeric, errors="raise")

# Ensure every pair uses the same complete observations.
if not np.isfinite(values.to_numpy()).all():
    raise ValueError("The input contains missing or infinite values.")

if (values.std() == 0).any():
    raise ValueError("A constant series cannot be used for correlation.")

# Calculate the Pearson correlation matrix.
correlation = values.corr(method="pearson")

correlation.to_csv(
    OUTPUT_DIR / "currency_correlation_matrix.csv",
    index_label="currency",
    float_format="%.6f"
)

# List each distinct currency pair once.
pair_results = []

for currency_1, currency_2 in combinations(CURRENCIES, 2):
    coefficient = correlation.loc[currency_1, currency_2]

    pair_results.append({
        "currency_1": currency_1,
        "currency_2": currency_2,
        "correlation": coefficient,
        "absolute_correlation": abs(coefficient)
    })

pairs = pd.DataFrame(pair_results)

# Rank pairs by the strength of their linear relationship.
pairs = pairs.sort_values(
    "absolute_correlation",
    ascending=False
).reset_index(drop=True)

pairs.to_csv(
    OUTPUT_DIR / "currency_pair_correlations.csv",
    index=False,
    float_format="%.6f"
)

# Draw a heatmap with a fixed scale from -1 to 1.
fig, ax = plt.subplots(figsize=(9, 8))

heatmap = ax.imshow(
    correlation.to_numpy(),
    cmap="RdBu_r",
    vmin=-1,
    vmax=1
)

ax.set_xticks(range(len(CURRENCIES)))
ax.set_yticks(range(len(CURRENCIES)))
ax.set_xticklabels(CURRENCIES)
ax.set_yticklabels(CURRENCIES)

# Display the coefficient in each cell.
for row in range(len(CURRENCIES)):
    for column in range(len(CURRENCIES)):
        coefficient = correlation.iloc[row, column]

        ax.text(
            column,
            row,
            f"{coefficient:.2f}",
            ha="center",
            va="center",
            color="white" if abs(coefficient) > 0.6 else "black"
        )

ax.set_title(
    "Pearson Correlation of Daily Log Changes\n"
    "Foreign Currency Units per EUR, 2010–2025"
)

fig.colorbar(
    heatmap,
    ax=ax,
    label="Pearson correlation",
    shrink=0.85
)

fig.tight_layout()
fig.savefig(
    FIGURE_DIR / "currency_correlation_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close(fig)

print("Observations used:", len(values))
print("Number of distinct currency pairs:", len(pairs))

print("\nCorrelation matrix:")
print(correlation.round(3))

print("\nFive strongest relationships:")
print(pairs.head(5).to_string(index=False))

print("\nFive weakest relationships:")
print(
    pairs.sort_values("absolute_correlation")
    .head(5)
    .to_string(index=False)
)

print("\nResults saved to:", OUTPUT_DIR)