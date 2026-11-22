# Parallel Computing Performance Experiment

## Workload and method

The experiment computes 60-observation rolling Pearson correlations for all 28 pairs of eight currencies, using 4096 daily log-return observations from the 2010-2025 dataset. Each configuration is measured 10 times, with method order rotated between repetitions. The same calculation function is used throughout. All results match the serial reference within rtol=1e-10 and atol=1e-12.

Fresh-pool timing includes process startup, data transfer, computation, result collection and shutdown. Reused-pool timing includes data transfer, computation and collection, but excludes startup, warm-up and shutdown. CSV I/O and correctness validation are excluded from every timed run. Batching uses 14 pairs per chunk with two workers and seven with four workers.

## Results

| Comparison workers | Method | Median (ms) | Speedup |
|---|---|---:|---:|
| 2 | Fresh pool | 711.785 | 0.015 |
| 2 | Reused pool | 9.232 | 1.120 |
| 2 | Reused + batched | 8.936 | 1.157 |
| 2 | Serial | 10.338 | 1.000 |
| 4 | Fresh pool | 818.837 | 0.013 |
| 4 | Reused pool | 7.390 | 1.394 |
| 4 | Reused + batched | 5.119 | 2.013 |
| 4 | Serial | 10.304 | 1.000 |

The fastest task-stage configuration is Reused + batched with 4 workers: 5.119 ms and 2.01x speedup, corresponding to a 50.3% reduction in task-stage elapsed time relative to its serial baseline.

Fresh-pool execution remains much slower than serial execution. The results are consistent with process setup overhead dominating this small workload. Reusing workers substantially reduces elapsed time, and batching further improves the measured task-stage median. The experiment does not separately isolate startup, serialization, scheduling and computation costs.

## Setup costs and interpretation

- 2 workers: startup plus one full warm-up workload = 0.681 s; shutdown = 0.102 s. These are single measurements, not repeated medians.
- 4 workers: startup plus one full warm-up workload = 0.755 s; shutdown = 0.107 s. These are single measurements, not repeated medians.

Serial execution is preferable for a single invocation of this small analysis. An already prepared persistent pool can improve the task-stage runtime when reused. The reported warm-pool speedup must not be described as an end-to-end application speedup; the total benefit across repeated workloads depends on how setup costs are amortized.

## Limitations

These measurements describe one machine, dataset and execution session. Ten repetitions and min-max whiskers describe observed variability, not confidence intervals or statistical significance. Millisecond timings are sensitive to system load. An idle persistent pool remains allocated during serial and fresh-pool measurements. No conclusion about large-scale or distributed scalability follows from this experiment.

## Figures

- ../data/analysis_output/figures/parallel_one_shot_runtime.png
- ../data/analysis_output/figures/parallel_reused_pool_runtime.png
- ../data/analysis_output/figures/parallel_reused_pool_speedup.png

Environment and exact timing definitions: ../data/analysis_output/pool_reuse_environment.csv
