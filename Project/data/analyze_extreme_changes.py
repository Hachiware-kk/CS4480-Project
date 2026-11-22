"""Empirical daily log-change distributions and largest absolute changes."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUTPUT = Path(__file__).resolve().parent / "analysis_output"
CURRENCIES = ["CNY", "USD", "JPY", "GBP", "HKD", "CHF", "AUD", "CAD"]
TOP_N = 10


def main():
    frame = pd.read_csv(OUTPUT / "fx_daily_log_returns_2010_2025.csv", parse_dates=["Date"])
    if frame["Date"].isna().any() or not frame["Date"].is_unique or not frame["Date"].is_monotonic_increasing:
        raise ValueError("Dates must be valid, unique and sorted.")
    values = frame.set_index("Date")[CURRENCIES] * 100
    if len(values) < TOP_N or not np.isfinite(values.to_numpy()).all():
        raise ValueError("At least ten finite observations per currency are required.")
    summary, events = [], []
    for currency in CURRENCIES:
        s = values[currency]
        q01, q05, q95, q99 = s.quantile([0.01, 0.05, 0.95, 0.99], interpolation="linear")
        lower, upper = s[s <= q01], s[s >= q99]
        summary.append({"currency": currency, "observations": len(s),
                        "q01_log_change_pct": q01, "q05_log_change_pct": q05,
                        "q95_log_change_pct": q95, "q99_log_change_pct": q99,
                        "lower_1pct_tail_mean_pct": lower.mean(), "lower_tail_count": len(lower),
                        "upper_1pct_tail_mean_pct": upper.mean(), "upper_tail_count": len(upper),
                        "min_log_change_pct": s.min(), "min_date": s.idxmin(),
                        "max_log_change_pct": s.max(), "max_date": s.idxmax(),
                        "abs_change_ge_1pct_count": int((s.abs() >= 1).sum()),
                        "abs_change_ge_1pct_share_pct": (s.abs() >= 1).mean() * 100})
        # Stable sorting breaks tied magnitudes in chronological order.
        top = s.abs().sort_values(ascending=False, kind="stable").head(TOP_N)
        for rank, date in enumerate(top.index, 1):
            change = s.loc[date]
            events.append({"currency": currency, "absolute_change_rank": rank, "Date": date,
                           "daily_log_change_pct": change, "absolute_log_change_pct": abs(change),
                           "simple_quote_change_pct": np.expm1(change / 100) * 100,
                           "eur_direction": "appreciation" if change > 0 else "depreciation" if change < 0 else "unchanged"})
    summary = pd.DataFrame(summary)
    summary.to_csv(OUTPUT / "extreme_daily_change_summary.csv", index=False, float_format="%.8f", date_format="%Y-%m-%d")
    pd.DataFrame(events).to_csv(OUTPUT / "top10_absolute_daily_changes.csv", index=False, float_format="%.8f", date_format="%Y-%m-%d")
    # Shared bins and axes retain extreme observations instead of clipping tails.
    bins = np.linspace(values.to_numpy().min(), values.to_numpy().max(), 101)
    fig, axes = plt.subplots(4, 2, figsize=(14, 13), sharex=True, sharey=True, constrained_layout=True)
    for ax, currency in zip(axes.flat, CURRENCIES):
        ax.hist(values[currency], bins=bins, color="steelblue", log=True)
        ax.axvline(values[currency].quantile(0.01), color="firebrick", linestyle="--", label="1st / 99th percentile")
        ax.axvline(values[currency].quantile(0.99), color="firebrick", linestyle="--")
        ax.set_title(currency)
        ax.set_xlabel("Daily log change (%)")
        ax.set_ylabel("Observation count (log scale)")
        ax.legend(fontsize=8)
    fig.suptitle("Daily Change Distributions and Empirical Tails\nForeign currency units per EUR; full observed range", fontsize=15)
    (OUTPUT / "figures").mkdir(exist_ok=True)
    fig.savefig(OUTPUT / "figures" / "daily_change_distributions.png", dpi=180)
    plt.close(fig)
    print(summary.to_string(index=False))
    print("Saved ten largest absolute changes per currency (80 rows).")


if __name__ == "__main__":
    main()
