# Exploratory Analysis Notes

## Dataset
- Period: 2010–2025
- Base currency: EUR
- Quote definition: Foreign currency units per 1 EUR
- Currencies: CNY, USD, JPY, GBP, HKD, CHF, AUD, CAD
- Daily log change: ln(P_t / P_previous)
- Positive changes indicate EUR appreciation against the quoted currency.

## 1. Descriptive Statistics
Source: ../data/analysis_output/daily_returns_summary.csv

- Currency with the highest daily volatility: JPY
- Daily volatility (%): 0.642004
- Currency with the lowest daily volatility: CHF
- Daily volatility (%): 0.463204

## 2. Exchange Rate Trends and Daily Changes
Figures:
- ../data/analysis_output/figures/indexed_exchange_rates.png
- ../data/analysis_output/figures/daily_log_returns.png

- Main observations from the indexed exchange rates: With 2010-01-04 = 100, the 2025-12-31 indices are CNY 83.737454, USD 81.659601, JPY 137.771292, GBP 97.890958, HKD 81.951115, CHF 62.623546, AUD 110.676739 and CAD 107.590450. EUR strengthened over these endpoints against JPY, AUD and CAD, and weakened against the other five currencies. Endpoint changes do not imply monotonic trends.
- Periods with visibly large daily changes: CHF on 2015-01-15 (-15.553938% log change) and 2011-09-06 (+7.996655%); JPY (-6.123226%) and GBP (+5.282616%) on 2016-06-24. These dates are identified numerically from the daily series.
- Observations requiring further investigation: CHF combines low full-period daily volatility with the largest absolute daily move. Investigate sensitivity to extreme observations; any policy or event explanation requires external evidence.

## 3. Correlation Analysis
Source: ../data/analysis_output/currency_pair_correlations.csv

- Pair with the largest absolute correlation: USD-HKD
- Correlation coefficient, including its sign: +0.996567
- Interpretation: USD and HKD daily log changes show nearly identical linear co-movement relative to EUR; this does not establish causation.

- Pair with the smallest absolute correlation: CHF-AUD
- Correlation coefficient, including its sign: +0.106444
- Interpretation: CHF and AUD have weak positive full-period linear co-movement; low correlation does not prove independence.

- Are any correlations negative? No; all 28 full-period pairwise correlations are positive.
- If yes, which pairs and what are their coefficients? Not applicable to the full-period matrix. Some rolling correlations are negative.

## Interpretation Limits
- All exchange rates share EUR as their base currency.
- Correlation does not establish causation.
- Full-period correlations may hide changes over time.



## 4. Currency Clustering

Method:
- Hierarchical clustering with average linkage.
- Distance: sqrt(2 * (1 - Pearson correlation)).
- Input: daily log changes of exchange rates quoted per EUR,
  covering 2010–2025.

Findings:
- USD and HKD merged first at a distance of approximately 0.083.
- CNY subsequently joined the USD–HKD cluster.
- AUD and CAD formed another relatively close pair.
- CHF merged with the remaining currencies last.
- JPY joined the CNY–USD–HKD cluster at a higher distance,
  indicating a weaker similarity than that within its core group.

Limitations:
- The partitions into 2, 3 and 4 clusters are exploratory.
- No optimal number of clusters has been established.
- Results depend on the observation period, common EUR base,
  distance definition and linkage method.
- Full-period clustering does not establish stability over time.

## 5. Monthly Exchange-Rate Changes and Calendar Heatmaps

Script: `../data/analyze_monthly_changes.py`

Method:
- Take the last available exchange-rate observation in each calendar month.
- Monthly simple quote change (%) = 100 * (current month-end rate / previous month-end rate - 1).
- This is a simple percentage change, unlike the daily log changes used elsewhere. Do not sum daily log percentages and label the result a simple monthly percentage.
- January 2010 has no preceding month in the cleaned dataset. Keep its value blank with status `missing_previous_month`; do not replace it with zero or a partial-month estimate.
- All eight currencies have 191 valid changes, February 2010 through December 2025. Month-end means the last observed date, not necessarily the final calendar day.

Outputs under `../data/analysis_output/`:
- `monthly_exchange_rate_changes.csv`: 1,536 rows (192 months x 8 currencies), with month, currency, previous/current observation dates, observation count, month-end quote, simple percentage change and availability status. Eight January 2010 changes are unavailable.
- `monthly_change_summary.csv`: eight rows, with valid count, arithmetic mean, median, sample standard deviation, positive/negative/zero month counts, and minimum/maximum months and changes. The mean is not a compounded growth rate; the standard deviation is not annualized.
- `figures/monthly_exchange_rate_heatmaps.png`: eight year-by-month heatmaps sharing one symmetric color scale. Red means EUR appreciation, blue means EUR depreciation, and gray means unavailable.

Findings:
- JPY has the largest standard deviation of monthly simple quote changes (2.894551%); CHF has the smallest (1.798148%).
- CHF has the most negative single monthly change among the eight currencies: -12.940785% in January 2015.
- JPY has the largest positive monthly change: +8.546783% in January 2013; GBP increased +8.485922% in June 2016.
- JPY has 113 positive and 78 negative months; CHF has 85 positive, 105 negative and one unchanged month. Signs refer to EUR's direction against the named currency.

Interpretation limits:
- Calendar heatmaps reveal timing and concentration, but do not establish recurring seasonality or event causation.
- Monthly aggregation can conceal large offsetting daily changes.
- Compounding the 191 monthly changes covers the January 2010 month-end to December 2025 month-end, not the first daily observation in January 2010.

## 6. Extreme Daily Changes and Distribution Tails

Script: `../data/analyze_extreme_changes.py`

Method:
- Use 4,096 daily log changes per currency, in percent: 100 * ln(P_t / P_previous).
- Compute empirical 1st, 5th, 95th and 99th percentiles with linear interpolation.
- Lower-tail mean averages observations at or below the 1st percentile; upper-tail mean averages observations at or above the 99th percentile. Each tail currently contains 41 observations per currency; ties can change this count in other datasets.
- Count observations with absolute log change >= 1 percentage point, using the same fixed threshold for every currency. This is a descriptive threshold, not a fitted outlier rule.
- Rank the ten largest absolute changes separately for each currency, retaining the sign and date; tied magnitudes use chronological order.
- Convert a log percentage x to a simple quote percentage with 100 * (exp(x / 100) - 1). Large log and simple percentages are not interchangeable.

Outputs under `../data/analysis_output/`:
- `extreme_daily_change_summary.csv`: eight rows containing quantiles, tail means/counts, extrema/dates and threshold exceedance counts/shares.
- `top10_absolute_daily_changes.csv`: 80 rows with currency, within-currency rank, date, signed/absolute log percentage, equivalent simple quote percentage and EUR direction. It is not the top 80 unique market dates.
- `figures/daily_change_distributions.png`: eight histograms with shared bins and axes, full observed range, logarithmic count scale and 1st/99th percentile markers. Empty bins have no visible bar on the log scale; distant tails are retained.

Findings:
- CHF has the largest absolute daily log change: -15.553938% on 2015-01-15. Its largest positive change is +7.996655% on 2011-09-06.
- CHF nevertheless has the lowest share of absolute log changes >= 1%: 101 / 4,096 = 2.465820%. This distinguishes the frequency of large changes from the size of the most extreme observation.
- JPY has the highest share above this threshold: 416 / 4,096 = 10.156250%.
- JPY's lower 1% tail mean is -2.391982%, compared with CHF's -1.928562%. A single worst observation and an average tail statistic answer different questions.
- GBP and JPY have opposite signed changes on 2016-06-24 (+5.282616% and -6.123226% respectively). No causal explanation is inferred from these dates alone.

Interpretation limits:
- These describe the observed sample, not future probabilities or portfolio losses. Quotes share EUR as their base, and these are not total investment returns.
- Quantiles depend on the sample and interpolation rule. The analysis does not assume normality or delete extreme observations.
- Daily changes compare successive available observations and may span weekends or holidays; they are not uniformly spaced 24-hour returns.

## 7. Reproduction and Verification

Run from the project root, using Python with numpy, pandas and matplotlib installed:

```powershell
python data/analyze_monthly_changes.py
python data/analyze_extreme_changes.py
```

Prerequisites are the existing cleaned exchange-rate CSV and daily log-return CSV. If absent, run `data/clean_exchange_rates.py` and then `data/calculate_returns.py` first. Both new scripts resolve paths relative to their own location and regenerate their outputs on each run without opening interactive plot windows.

Verification completed on the current data:
- Both scripts executed successfully; four CSVs and two PNG figures were produced.
- Monthly compounding matches the ratio of final to initial month-end quotes for all eight currencies.
- Monthly changes were independently checked against daily log changes recomputed from cleaned rates, summed by month and transformed by exp(sum) - 1, excluding the unavailable first month. The existing daily-return CSV has rounding (maximum absolute log-unit difference about 5e-8 from recomputed values), so it is not used for this strict monthly identity check. Extreme-change analysis consistently uses that existing daily-return CSV.
- Extreme minima/maxima match the existing descriptive statistics; top-ten magnitudes and event counts were checked against the input daily changes.
- Dates are validated as unique and sorted, and required numeric inputs must be finite (exchange-rate levels must also be positive).
