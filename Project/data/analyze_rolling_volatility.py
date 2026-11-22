from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


OUTPUT = Path(__file__).resolve().parent / "analysis_output"
CURRENCIES = ["CNY", "USD", "JPY", "GBP", "HKD", "CHF", "AUD", "CAD"]
WINDOW = 60


def main():
    df = pd.read_csv(
        OUTPUT / "fx_daily_log_returns_2010_2025.csv", parse_dates=["Date"]
    ).set_index("Date")
    if df.index.hasnans or not df.index.is_unique or not df.index.is_monotonic_increasing:
        raise ValueError("Dates must be valid, unique and sorted.")
    if len(df) < WINDOW or not np.isfinite(df[CURRENCIES].to_numpy()).all():
        raise ValueError("Input must contain enough finite observations.")
    # Daily volatility in percent, not annualized volatility.
    rolling = df[CURRENCIES].rolling(WINDOW, min_periods=WINDOW).std(ddof=1) * 100
    rolling = rolling.iloc[WINDOW - 1:]
    if not np.isfinite(rolling.to_numpy()).all():
        raise ValueError("Invalid rolling volatility results.")
    np.testing.assert_allclose(
        rolling.iloc[0].to_numpy(),
        df[CURRENCIES].iloc[:WINDOW].std(ddof=1).to_numpy() * 100,
        rtol=1e-10, atol=1e-12
    )
    rolling.to_csv(OUTPUT / "rolling_daily_volatility_60d_pct.csv", index_label="Date", float_format="%.6f")
    rows = []
    for currency in CURRENCIES:
        series = rolling[currency]
        peak_date = series.idxmax()
        peak_position = df.index.get_loc(peak_date)
        rows.append({
            "currency": currency,
            "valid_windows": len(series),
            "mean_rolling_daily_volatility_pct": series.mean(),
            "min_daily_volatility_pct": series.min(),
            "min_window_end": series.idxmin().strftime("%Y-%m-%d"),
            "max_daily_volatility_pct": series.max(),
            "max_window_start": df.index[peak_position - WINDOW + 1].strftime("%Y-%m-%d"),
            "max_window_end": peak_date.strftime("%Y-%m-%d"),
        })
    summary = pd.DataFrame(rows)
    summary.to_csv(OUTPUT / "rolling_volatility_summary_60d.csv", index=False, float_format="%.6f")

    fig, axes = plt.subplots(4, 2, figsize=(14, 12), sharex=True, sharey=True)
    for ax, currency in zip(axes.flat, CURRENCIES):
        ax.plot(rolling.index, rolling[currency], linewidth=0.8)
        ax.set_title(currency)
        ax.set_ylabel("Daily volatility (%)")
        ax.set_ylim(0, float(rolling.to_numpy().max()) * 1.05)
        ax.grid(alpha=0.25)
    fig.suptitle("60-Observation Rolling Volatility of Daily Log Changes\nForeign Currency Units per EUR, 2010–2025; not annualized")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    (OUTPUT / "figures").mkdir(exist_ok=True)
    fig.savefig(OUTPUT / "figures" / "rolling_daily_volatility_60d.png", dpi=200)
    plt.close(fig)
    print(summary.to_string(index=False))
    print("\nFirst-window calculation verified against a direct sample standard deviation.")


if __name__ == "__main__":
    main()
