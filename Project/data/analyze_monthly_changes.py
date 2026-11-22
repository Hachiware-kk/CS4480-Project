"""Month-end percentage changes and calendar heatmaps of EUR-based quotes."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent
OUTPUT = DATA / "analysis_output"
CURRENCIES = ["CNY", "USD", "JPY", "GBP", "HKD", "CHF", "AUD", "CAD"]


def main():
    rates = pd.read_csv(DATA / "cleaning_output" / "fx_eur_8currencies_2010_2025.csv",
                        parse_dates=["Date"]).set_index("Date")[CURRENCIES]
    if rates.empty or rates.index.hasnans or not rates.index.is_unique or not rates.index.is_monotonic_increasing:
        raise ValueError("Dates must be nonempty, valid, unique and sorted.")
    if not np.isfinite(rates.to_numpy()).all() or (rates <= 0).any().any():
        raise ValueError("Exchange rates must be finite and positive.")
    periods = rates.index.to_period("M")
    expected = pd.period_range(periods.min(), periods.max(), freq="M")
    month_end = rates.groupby(periods).last().reindex(expected)
    if month_end.isna().any().any():
        raise ValueError("Missing calendar months in input.")
    # January 2010 is unavailable: December 2009 is outside the cleaned sample.
    changes = month_end.pct_change(fill_method=None) * 100
    observations = rates.groupby(periods).size().reindex(expected)
    last_dates = pd.Series(rates.index, index=periods).groupby(level=0).last().reindex(expected)
    rows, summaries = [], []
    for currency in CURRENCIES:
        for month in expected:
            previous = month - 1
            rows.append({"month": str(month), "currency": currency,
                         "previous_observation_date": last_dates.get(previous, pd.NaT),
                         "last_observation_date": last_dates.loc[month],
                         "rate_observations_in_month": int(observations.loc[month]),
                         "month_end_rate": month_end.loc[month, currency],
                         "monthly_change_pct": changes.loc[month, currency],
                         "status": "missing_previous_month" if month == expected[0] else "available"})
        valid = changes[currency].dropna()
        if valid.empty:
            raise ValueError("At least two calendar months are required.")
        # Compounding all monthly changes must reproduce the endpoint ratio.
        np.testing.assert_allclose(np.prod(1 + valid / 100),
                                   month_end[currency].iloc[-1] / month_end[currency].iloc[0])
        summaries.append({"currency": currency, "valid_months": len(valid),
                          "mean_monthly_change_pct": valid.mean(),
                          "median_monthly_change_pct": valid.median(),
                          "monthly_std_pct": valid.std(ddof=1),
                          "positive_months": int((valid > 0).sum()),
                          "negative_months": int((valid < 0).sum()),
                          "zero_months": int((valid == 0).sum()),
                          "min_month": str(valid.idxmin()), "min_monthly_change_pct": valid.min(),
                          "max_month": str(valid.idxmax()), "max_monthly_change_pct": valid.max()})
    OUTPUT.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT / "monthly_exchange_rate_changes.csv", index=False,
                              float_format="%.8f", date_format="%Y-%m-%d")
    summary = pd.DataFrame(summaries)
    summary.to_csv(OUTPUT / "monthly_change_summary.csv", index=False, float_format="%.8f")
    years = sorted(set(expected.year))
    limit = float(np.nanmax(np.abs(changes.to_numpy())))
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("#dddddd")
    fig, axes = plt.subplots(4, 2, figsize=(15, 18), constrained_layout=True)
    for ax, currency in zip(axes.flat, CURRENCIES):
        matrix = changes[currency].groupby([expected.year, expected.month]).first().unstack().reindex(index=years, columns=range(1, 13))
        im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=-limit, vmax=limit)
        ax.set_title(currency)
        ax.set_xticks(range(12), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        ax.set_yticks(range(len(years)), years)
    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.6, label="Month-end quote change (%)")
    fig.suptitle("Monthly Changes in Foreign Currency Units per EUR\nRed: EUR appreciation; blue: EUR depreciation; gray: unavailable", fontsize=15)
    (OUTPUT / "figures").mkdir(exist_ok=True)
    fig.savefig(OUTPUT / "figures" / "monthly_exchange_rate_heatmaps.png", dpi=180)
    plt.close(fig)
    print(summary.to_string(index=False))
    print("Monthly compounding verified against month-end exchange-rate ratios.")


if __name__ == "__main__":
    main()
