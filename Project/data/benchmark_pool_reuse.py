"""Compare one-shot and persistent pools on the same 28 rolling correlations."""
import math
import multiprocessing as mp
import os
import platform
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter

import numpy as np
import pandas as pd

from benchmark_rolling_correlations import (
    CURRENCIES, OUTPUT_DIR, WINDOW, calculate_pair,
)
from itertools import combinations

REPEATS = 10


def ready(barrier):
    # All workers must finish imports and start before warm-up can complete.
    barrier.wait(timeout=60)


def main():
    df = pd.read_csv(OUTPUT_DIR / "fx_daily_log_returns_2010_2025.csv",
                     parse_dates=["Date"])
    if (not df.Date.is_unique or not df.Date.is_monotonic_increasing
            or len(df) < WINDOW
            or not np.isfinite(df[CURRENCIES].to_numpy()).all()):
        raise ValueError("Invalid input data or dates.")
    tasks = [(f"{a}_{b}", df[a].to_numpy(), df[b].to_numpy())
             for a, b in combinations(CURRENCIES, 2)]
    reference = dict(map(calculate_pair, tasks))
    if not all(np.isfinite(x).all() for x in reference.values()):
        raise ValueError("Undefined reference correlations.")
    records, setups = [], []

    def check(result):
        if len(result) != len(reference) or set(dict(result)) != set(reference):
            raise AssertionError("Missing or duplicate pairs.")
        difference = 0.0
        for name, values in result:
            np.testing.assert_allclose(values, reference[name],
                                       rtol=1e-10, atol=1e-12)
            difference = max(difference, float(np.max(np.abs(values-reference[name]))))
        return difference

    ctx = mp.get_context("spawn")
    for workers in sorted({min(2, os.cpu_count() or 1), min(4, os.cpu_count() or 1)}):
        barrier = ctx.Barrier(workers)
        start = perf_counter()
        pool = ProcessPoolExecutor(max_workers=workers, mp_context=ctx,
                                   initializer=ready, initargs=(barrier,))
        try:
            warmup = list(pool.map(calculate_pair, tasks))
            setup_seconds = perf_counter() - start
            check(warmup)
            methods = ["serial", "fresh_pool", "reused_pool", "reused_pool_batched"]
            for repeat in range(1, REPEATS + 1):
                offset = (repeat - 1) % len(methods)
                for method in methods[offset:] + methods[:offset]:
                    chunksize = math.ceil(len(tasks)/workers) if method.endswith("batched") else 1
                    start = perf_counter()
                    if method == "serial":
                        result = list(map(calculate_pair, tasks))
                    elif method == "fresh_pool":
                        with ProcessPoolExecutor(max_workers=workers, mp_context=ctx) as fresh:
                            result = list(fresh.map(calculate_pair, tasks))
                    else:
                        result = list(pool.map(calculate_pair, tasks, chunksize=chunksize))
                    elapsed = perf_counter() - start
                    difference = check(result)  # Validation is outside timing.
                    records.append(dict(repeat=repeat, method=method,
                        comparison_workers=workers, workers=1 if method == "serial" else workers,
                        chunksize=chunksize, seconds=elapsed, pairs=len(tasks),
                        observations=len(df), window=WINDOW, results_match=True,
                        max_absolute_difference=difference))
                print(f"Workers={workers}, repeat={repeat}/{REPEATS} complete", flush=True)
        finally:
            start = perf_counter()
            pool.shutdown(wait=True)
            shutdown_seconds = perf_counter() - start
        setups.append(dict(workers=workers, startup_and_warmup_seconds=setup_seconds,
                           shutdown_seconds=shutdown_seconds))

    runs = pd.DataFrame(records)
    summary = runs.groupby(["comparison_workers", "method", "workers"], as_index=False).agg(
        runs=("seconds", "count"), median_seconds=("seconds", "median"),
        min_seconds=("seconds", "min"), max_seconds=("seconds", "max"),
        all_results_match=("results_match", "all"))
    baselines = summary[summary.method == "serial"].set_index("comparison_workers").median_seconds
    summary["speedup"] = summary.comparison_workers.map(baselines)/summary.median_seconds
    runs.to_csv(OUTPUT_DIR / "pool_reuse_benchmark_runs.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "pool_reuse_benchmark_summary.csv", index=False)
    pd.DataFrame(setups).to_csv(OUTPUT_DIR / "pool_reuse_setup_times.csv", index=False)
    metadata = dict(python=platform.python_version(), platform=platform.platform(),
                    logical_cpus=os.cpu_count(), numpy=np.__version__, pandas=pd.__version__,
                    repeats=REPEATS, start_method="spawn",
                    fresh_pool_scope="Startup, transfer, computation, collection, shutdown",
                    reused_pool_scope="Transfer, computation, collection; excludes setup and shutdown",
                    excluded="CSV I/O and correctness validation",
                    setup_scope="Startup plus one full untimed warm-up workload",
                    baseline="Serial median within the same comparison_workers group",
                    note="Persistent pool remains idle during serial/fresh measurements")
    pd.DataFrame(metadata.items(), columns=["key", "value"]).to_csv(
        OUTPUT_DIR / "pool_reuse_environment.csv", index=False)
    print(summary.to_string(index=False))
    print("Reused-pool speedups exclude startup/warm-up and shutdown; see setup CSV.")


if __name__ == "__main__":
    main()
