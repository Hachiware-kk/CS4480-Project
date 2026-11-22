from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DATA_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = DATA_DIR / "analysis_output"
FIGURE_DIR = OUTPUT_DIR / "figures"
CURRENCIES = ["CNY", "USD", "JPY", "GBP", "HKD", "CHF", "AUD", "CAD"]


def main():
    df = pd.read_csv(
        OUTPUT_DIR / "fx_daily_log_returns_2010_2025.csv", parse_dates=["Date"]
    )
    if df["Date"].isna().any() or not df["Date"].is_unique:
        raise ValueError("Dates must be valid and unique.")
    if not np.isfinite(df[CURRENCIES].to_numpy(dtype=float)).all():
        raise ValueError("Returns must be finite.")

    grouped = df.groupby(df["Date"].dt.year)[CURRENCIES]
    counts = grouped.count()
    if counts.min().min() < 2:
        raise ValueError("Each year needs at least two observations.")

    # Sample standard deviation of daily log returns, expressed as percent.
    annual = grouped.std(ddof=1) * 100
    annual.index.name = "year"
    annual.to_csv(
        OUTPUT_DIR / "annual_daily_volatility_pct_2010_2025.csv",
        float_format="%.6f"
    )
    counts.index.name = "year"
    counts.to_csv(OUTPUT_DIR / "annual_observation_counts.csv")

    FIGURE_DIR.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    annual.plot(ax=ax, marker="o", markersize=3, linewidth=1.4)
    ax.set_title("Annual Volatility of Daily Log Changes, 2010–2025")
    ax.set_xlabel("Year")
    ax.set_ylabel("Standard deviation of daily log changes (%)")
    ax.set_xticks(annual.index)
    ax.grid(alpha=0.25)
    ax.legend(title="Currency", ncol=4)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "annual_daily_volatility_pct.png", dpi=300)
    plt.close(fig)

    print("Years:", len(annual))
    print("Observations per year:", counts.iloc[:, 0].to_dict())
    print("Highest annual daily volatility:")
    year, currency = np.unravel_index(np.argmax(annual.to_numpy()), annual.shape)
    print(annual.index[year], annual.columns[currency],
          f"{annual.iloc[year, currency]:.4f}%")
    print("Saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
