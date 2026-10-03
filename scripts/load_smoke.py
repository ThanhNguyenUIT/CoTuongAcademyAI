"""Small, bounded local HTTP smoke; not a production capacity test."""

from __future__ import annotations

import argparse
import asyncio
import math
import statistics
import time
from collections import Counter
from uuid import uuid4

import httpx


STARTING_FEN = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1"


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(quantile * len(ordered)) - 1)]


async def run(args: argparse.Namespace) -> int:
    semaphore = asyncio.Semaphore(args.concurrency)
    latencies: list[float] = []
    statuses: Counter[str] = Counter()
    engine_ms: list[int] = []

    async with httpx.AsyncClient(base_url=args.base_url, timeout=args.timeout_seconds) as client:
        async def request(index: int) -> None:
            async with semaphore:
                started = time.perf_counter()
                try:
                    if args.mode == "health":
                        response = await client.get("/health")
                    else:
                        response = await client.post("/v1/engine/analyze", json={
                            "fen": STARTING_FEN,
                            "time_ms": args.engine_time_ms,
                            "depth": args.depth,
                            "multipv": 1,
                            "job_id": f"load-smoke-{uuid4().hex}-{index}",
                        })
                    latencies.append((time.perf_counter() - started) * 1000)
                    statuses[str(response.status_code)] += 1
                    if response.is_success and args.mode == "engine":
                        body = response.json()
                        if isinstance(body.get("elapsed_ms"), int):
                            engine_ms.append(body["elapsed_ms"])
                except httpx.HTTPError as exc:
                    latencies.append((time.perf_counter() - started) * 1000)
                    statuses[f"error:{type(exc).__name__}"] += 1

        total_started = time.perf_counter()
        await asyncio.gather(*(request(index) for index in range(args.requests)))
        total_ms = (time.perf_counter() - total_started) * 1000

    print(f"mode={args.mode} requests={args.requests} concurrency={args.concurrency} wall_ms={total_ms:.1f}")
    print(f"status_counts={dict(statuses)}")
    if latencies:
        print(f"client_latency_ms_p50={statistics.median(latencies):.1f} p95={percentile(latencies, .95):.1f} max={max(latencies):.1f}")
    if engine_ms:
        print(f"engine_elapsed_ms_p50={statistics.median(engine_ms):.1f} p95={percentile([float(x) for x in engine_ms], .95):.1f}")
    return 0 if len(statuses) == 1 and "200" in statuses else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--mode", choices=("health", "engine"), default="engine")
    parser.add_argument("--requests", type=int, default=12)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--engine-time-ms", type=int, default=300)
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--timeout-seconds", type=float, default=10)
    args = parser.parse_args()
    if not 1 <= args.requests <= 1000:
        parser.error("--requests must be between 1 and 1000")
    concurrency_limit = 3 if args.mode == "engine" else 100
    if not 1 <= args.concurrency <= concurrency_limit:
        parser.error(f"--concurrency must be between 1 and {concurrency_limit} for {args.mode} mode")
    if not 100 <= args.engine_time_ms <= 5000 or not 1 <= args.depth <= 20:
        parser.error("engine limits exceed the API request bounds")
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    return args


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run(parse_args())))
