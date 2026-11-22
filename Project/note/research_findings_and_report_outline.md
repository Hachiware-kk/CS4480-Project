# Research Findings and Report Outline

Working title: Exploring EUR-Based Exchange Rates: Correlation, Volatility, Clustering and Parallel Computing

This is an evidence-based writing plan, not the final report. Values refer to the current saved CSV outputs.

## 1. Research questions

1. How do daily exchange-rate changes and volatility differ across the eight currencies?
2. Which currencies move together, and how stable are these relationships over time?
3. What groups emerge from correlation-based hierarchical clustering?
4. How do process-pool reuse and task batching affect rolling-correlation runtime?

## 2. Dataset facts

- Eight quote currencies: CNY, USD, JPY, GBP, HKD, CHF, AUD and CAD; EUR is the common base.
- Requested period: 2010-01-01 to 2025-12-31. Actual retained observations: 2010-01-04 to 2025-12-31.
- The cleaning summary records 7,141 original rows, 3,044 outside the requested period, 4,097 retained rows, zero exact duplicates removed and zero retained rows with missing rates.
- Differencing yields 4,096 log-return observations per currency. A 60-observation window yields 4,037 valid windows per pair.
- Quotes are foreign currency units per EUR. A positive log change means EUR appreciation against that quote currency. These are exchange-rate log changes, not total investment returns.
- Evidence: `data/cleaning_output/cleaning_summary.csv` and `data/analysis_output/daily_returns_summary.csv`.

## 3. Findings and evidence

| Finding | Numerical evidence | Source under data/analysis_output | Interpretation boundary |
|---|---|---|---|
| JPY has the highest full-period daily volatility; CHF has the lowest | JPY: 0.642004%; CHF: 0.463204% | daily_returns_summary.csv | Standard deviation of daily log changes; not annualized volatility |
| Low full-period volatility does not rule out extreme local volatility | CHF has the highest maximum 60-observation daily volatility among the eight currencies: 2.107576%, window 2015-01-15 to 2015-04-10 | rolling_volatility_summary_60d.csv | A window statistic, not a single-day return or a causal explanation |
| USD and HKD move almost identically relative to EUR | Full-period correlation: 0.996567; rolling correlation: 0.916335 to 0.999986 | currency_pair_correlations.csv; rolling_correlation_summary_all_pairs_60d.csv | Common EUR base affects the interpretation |
| CHF and AUD have the weakest full-period absolute correlation among the 28 pairs | 0.106444; all 28 full-period correlations are positive | currency_pair_correlations.csv | Weak linear correlation does not establish independence |
| Full-period correlations hide changes in sign and strength | JPY-AUD: full-period 0.146437; rolling minimum -0.600930 and maximum 0.807684 | rolling_correlation_summary_all_pairs_60d.csv | Rolling dates mark window endpoints; overlapping windows are dependent |
| USD-HKD is the most stable pair by rolling-correlation standard deviation; USD-JPY is the least stable by that metric | Standard deviations: 0.009220 and 0.272307, respectively | rolling_correlation_summary_all_pairs_60d.csv | Stability is defined by this metric, not by range alone |
| Clustering summarizes the correlation structure | USD-HKD merges first at distance 0.082864, CNY joins next; AUD-CAD also forms a pair; CHF joins last | currency_cluster_linkage.csv; figures/currency_clustering_dendrogram.png | Average linkage with distance sqrt(2*(1-r)); exploratory, not independent confirmation of correlation |
| Parallel benefits depend on timing scope | Four-worker serial: 10.30375 ms; fresh pool: 818.83705 ms; reused and batched: 5.11850 ms, speedup 2.01304x | pool_reuse_benchmark_summary.csv | Warm-pool speedup excludes setup and shutdown; one-shot execution remains slower than serial |

## 4. Suggested report structure

The supplied slides provide a project example and assessment criteria, but do not specify a mandatory report template or page limit. The structure below is a proposed organization.

| Section | Main content | Suggested evidence |
|---|---|---|
| 1. Introduction and objectives | Motivate studying co-movement, changing volatility and computational overhead; state the four research questions | Brief project scope |
| 2. Data source and preprocessing | Source provenance, date and currency selection, missing-value checks, quote direction and log-change calculation | Cleaning summary; preprocessing code |
| 3. Exploratory analysis | Indexed exchange-rate trends, daily changes, descriptive statistics and full-period correlation | Indexed trends, daily-change plots, correlation heatmap |
| 4. Time-varying relationships and clustering | Annual and rolling volatility; all-pair rolling correlations; hierarchical clustering | Volatility figures, rolling summary and dendrogram |
| 5. Parallel implementation and performance | Independent pair tasks; serial baseline; 2/4 workers; pool reuse; batching; correctness checks; timing definitions; repeated measurements | Three performance figures and benchmark tables |
| 6. Discussion and limitations | Answer research questions; distinguish observed patterns from explanations; common-base effects, window choice, outliers, small workload and single-machine limits | Findings table above |
| 7. Conclusion and future work | Summarize supported findings; propose window sensitivity, outlier sensitivity and meaningful workload scaling as future work | No unperformed experiment presented as completed |
| References and reproducibility | Verified data citation, method sources, software versions, execution instructions and relevant acknowledgements | Environment CSV and source files |

## 5. Assessment alignment

Transcribed from `sources/d4b30603b8ba1cec4b015d642585c9b2.png`:

| Criterion | Points | Planned evidence |
|---|---:|---|
| Real World Impact / Creativity | 5 | Explain what changes in co-movement and volatility reveal; avoid unsupported investment claims |
| Solid Works and Output Amount | 20 | Reproducible cleaning, analyses, figures and benchmark outputs |
| Technical Depth and Correctness | 20 | Formulas, quote direction, clustering method, rolling-window definition, validation and limitations |
| Parallel Computing Elements | 20 | Explain implementation choices and both one-shot and warm-pool results |
| Use of Written English | 5 | Consistent terms, clear figure captions and evidence-based claims |
| Technical Presentation Amount | 20 | A later presentation covering methods, findings and performance |
| Technical Presentation Skills | 5 | A later rehearsal and clear allocation of speaking roles |
| Question and Answer (Q&A) | 5 | A later question bank addressing design choices and limitations |

This mapping identifies relevant evidence; it does not predict a grade. The provided slides do not state a minimum speedup requirement.

## 6. Remaining work before a final report

- Verify and cite the original data download source and record the actual download date if known. Do not infer it from file timestamps.
- Exploratory TODOs are now filled from saved data, including endpoint indices, daily extremes and correlations; review wording when preparing the final report.
- Integrate annual volatility findings into the narrative: CHF in 2015 has the highest annual daily standard deviation (1.066386%) in `annual_daily_volatility_pct_2010_2025.csv`; this is not annualized volatility.
- If linking observed movements to policy or economic events, obtain external sources and describe the connection as an interpretation unless causal evidence is available.
- Add exact formulas and implementation details, including the sample-standard-deviation convention used by the scripts.
- Document execution order and software dependencies, and check the main figures against the final saved outputs.
- Check any additional Canvas instructions for page limits, submission format and presentation length; these are absent from the six supplied images.
- Review the text, record actual contributions and assistance accurately, then prepare the final report and presentation.

## 7. Suggested central argument

The eight EUR-based exchange-rate series exhibit heterogeneous volatility and correlation patterns. Strong full-period co-movement can remain stable, as for USD-HKD, while weaker aggregate correlations can conceal substantial time variation, as for JPY-AUD. Clustering summarizes these relationships but does not establish their causes. For the computational component, process setup dominates one-shot execution of this small workload, whereas reusing a prepared pool and batching tasks achieves approximately twofold task-stage acceleration in the saved four-worker experiment.


## 8. Additional Completed Analyses

Two supplementary analyses now extend the evidence for research question 1:

| Analysis | Script under data/ | Evidence under data/analysis_output/ | Report use |
|---|---|---|---|
| Monthly changes and calendar heatmaps | analyze_monthly_changes.py | monthly_exchange_rate_changes.csv; monthly_change_summary.csv; figures/monthly_exchange_rate_heatmaps.png | Add to exploratory analysis: compare direction and timing across months, without claiming seasonality |
| Empirical tails and extreme dates | analyze_extreme_changes.py | extreme_daily_change_summary.csv; top10_absolute_daily_changes.csv; figures/daily_change_distributions.png | Add to discussion: distinguish typical volatility, frequency of large changes and severity of extremes |

- Monthly changes use simple month-end percentages; January 2010 is unavailable because the preceding month is outside the cleaned sample. Each currency has 191 valid changes.
- CHF's January 2015 monthly change is -12.940785%. JPY has the highest monthly standard deviation (2.894551%).
- CHF's worst daily log change is -15.553938% on 2015-01-15, despite having the lowest full-period daily standard deviation. Its absolute-log-change >= 1% frequency is 2.465820%, versus JPY's 10.156250%.
- These additions are serial descriptive analyses. They do not change the scope, measured timings or conclusions of the existing parallel benchmarks.
- Methods, field definitions, limitations and reproduction commands are documented in sections 5-7 of `exploratory_analysis_notes.md`.
