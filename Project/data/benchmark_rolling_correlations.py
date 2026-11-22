import os
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd


OUTPUT_DIR = Path(__file__).resolve().parent / "analysis_output"
CURRENCIES = ["CNY", "USD", "JPY", "GBP", "HKD", "CHF", "AUD", "CAD"]
WINDOW = 60
REPEATS = 5


def calculate_pair(task):
    name, first, second = task
    result = pd.Series(first).rolling(WINDOW, min_periods=WINDOW).corr(
        pd.Series(second)
    ).to_numpy()[WINDOW - 1:]
    return name, result


def main():
    df = pd.read_csv(
        OUTPUT_DIR / "fx_daily_log_returns_2010_2025.csv", parse_dates=["Date"]
    )
    if not df["Date"].is_unique or not df["Date"].is_monotonic_increasing:
        raise ValueError("Dates must be unique and sorted.")
    if len(df) < WINDOW or not np.isfinite(df[CURRENCIES].to_numpy()).all():
        raise ValueError("Invalid input data.")
    tasks = [
        (f"{a}_{b}", df[a].to_numpy(), df[b].to_numpy())
        for a, b in combinations(CURRENCIES, 2)
    ]
    # Generate the reference and warm up the parent process before timing.
    reference = dict(map(calculate_pair, tasks))
    if not all(np.isfinite(values).all() for values in reference.values()):
        raise ValueError("Undefined correlations in the reference results.")

    worker_counts = sorted({min(2, os.cpu_count() or 1), min(4, os.cpu_count() or 1)})
    methods = [("serial", 1)] + [("parallel", n) for n in worker_counts]
    records = []
    for repeat in range(1, REPEATS + 1):
        # Rotate execution order to reduce systematic order effects.
        offset = (repeat - 1) % len(methods)
        for method, workers in methods[offset:] + methods[:offset]:
            start = perf_counter()
            if method == "serial":
                result = list(map(calculate_pair, tasks))
            else:
                # Include pool creation, transfer, computation and shutdown.
                with ProcessPoolExecutor(max_workers=workers) as executor:
                    result = list(executor.map(calculate_pair, tasks))
            elapsed = perf_counter() - start
            max_difference = 0.0
            for name, values in result:
                np.testing.assert_allclose(values, reference[name], rtol=1e-10, atol=1e-12)
                max_difference = max(max_difference, float(np.max(np.abs(values - reference[name]))))
            records.append({
                "repeat": repeat, "method": method, "workers": workers,
                "seconds": elapsed, "pairs": len(tasks), "window": WINDOW,
                "observations": len(df), "results_match": True,
                "max_absolute_difference": max_difference,
            })
            print(f"Repeat {repeat}: {method}, workers={workers}, {elapsed:.6f} seconds", flush=True)

    timings = pd.DataFrame(records)
    summary = timings.groupby(["method", "workers"], as_index=False).agg(
        runs=("seconds", "count"), median_seconds=("seconds", "median"),
        min_seconds=("seconds", "min"), max_seconds=("seconds", "max"),
        all_results_match=("results_match", "all"),
    )
    serial_time = summary.loc[summary["method"] == "serial", "median_seconds"].iloc[0]
    summary["speedup"] = serial_time / summary["median_seconds"]
    timings.to_csv(OUTPUT_DIR / "rolling_benchmark_runs.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "rolling_benchmark_summary.csv", index=False)
    print("\nTiming scope: computation including process pool startup, transfer and shutdown; excludes CSV I/O and validation.")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
