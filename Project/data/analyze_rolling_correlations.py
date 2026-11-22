from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DATA_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = DATA_DIR / "analysis_output"
FIGURE_DIR = OUTPUT_DIR / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = OUTPUT_DIR / "fx_daily_log_returns_2010_2025.csv"

WINDOW = 60

PAIRS = [
    ("USD", "HKD"),
    ("CNY", "USD"),
    ("AUD", "CAD"),
    ("AUD", "JPY"),
]


def main():
    # Read daily log changes and use dates as the index.
    df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])
    df = df.set_index("Date")

    if not df.index.is_monotonic_increasing:
        raise ValueError("Dates must be in ascending order.")

    if not df.index.is_unique:
        raise ValueError("Dates must be unique.")

    currencies = sorted({currency for pair in PAIRS for currency in pair})
    values = df[currencies].to_numpy(dtype=float)

    if not np.isfinite(values).all():
        raise ValueError("The input contains missing or infinite values.")

    if len(df) < WINDOW:
        raise ValueError("There are not enough observations.")

    # Calculate one rolling correlation series for each selected pair.
    rolling_results = pd.DataFrame(index=df.index)

    for currency_1, currency_2 in PAIRS:
        pair_name = f"{currency_1}_{currency_2}"

        rolling_results[pair_name] = (
            df[currency_1]
            .rolling(window=WINDOW, min_periods=WINDOW)
            .corr(df[currency_2])
        )

    # The first WINDOW - 1 rows do not have a complete window.
    rolling_results = rolling_results.iloc[WINDOW - 1:]

    rolling_results.to_csv(
        OUTPUT_DIR / "rolling_correlations_60d.csv",
        index_label="Date",
        float_format="%.6f",
    )

    # Summarize the rolling correlations.
    summary_rows = []

    for pair_name in rolling_results.columns:
        series = rolling_results[pair_name].dropna()

        if series.empty:
            raise ValueError(f"No valid correlations for {pair_name}.")

        summary_rows.append({
            "pair": pair_name,
            "valid_windows": len(series),
            "mean_correlation": series.mean(),
            "std_correlation": series.std(),
            "min_correlation": series.min(),
            "min_date": series.idxmin().strftime("%Y-%m-%d"),
            "max_correlation": series.max(),
            "max_date": series.idxmax().strftime("%Y-%m-%d"),
        })

    summary = pd.DataFrame(summary_rows)

    summary.to_csv(
        OUTPUT_DIR / "rolling_correlation_summary_60d.csv",
        index=False,
        float_format="%.6f",
    )

    # Use separate panels with the same vertical scale.
    fig, axes = plt.subplots(
        2, 2, figsize=(14, 8), sharex=True, sharey=True
    )

    for ax, (currency_1, currency_2) in zip(axes.flat, PAIRS):
        pair_name = f"{currency_1}_{currency_2}"

        ax.plot(
            rolling_results.index,
            rolling_results[pair_name],
            linewidth=0.9,
        )

        full_period_corr = df[currency_1].corr(df[currency_2])

        ax.axhline(
            full_period_corr,
            color="darkorange",
            linestyle="--",
            linewidth=1.2,
            label=f"Full-period correlation: {full_period_corr:.3f}",
        )

        ax.axhline(0, color="gray", linewidth=0.7)
        ax.set_title(f"{currency_1} and {currency_2}")
        ax.set_ylim(-1.05, 1.05)
        ax.set_ylabel("Pearson correlation")
        ax.grid(alpha=0.25)
        ax.legend(loc="lower left", fontsize=8)

    fig.suptitle(
        "60-Observation Rolling Correlations of Daily Log Changes\n"
        "Foreign Currency Units per EUR, 2010-2025"
    )

    fig.autofmt_xdate()
    fig.tight_layout(rect=(0, 0, 1, 0.93))

    fig.savefig(
        FIGURE_DIR / "rolling_correlations_60d.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)

    print("Window size:", WINDOW)
    print("Window end dates:", len(rolling_results))
    print("\nRolling correlation summary:")
    print(summary.to_string(index=False))
    print("\nResults saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()