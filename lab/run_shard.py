"""Backtest one shard of the pool, each strategy alone, in both periods.
Usage: python -m lab.run_shard <runnable.json> <shard> <shards> <config.json> <pool> <outdir>
Writes <outdir>/<strategy>.json: per period, a summary and the daily profit series (or the error)."""
import json
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import resource

from .settings import BACKTEST_TIMEOUT, FEE, MEMORY_LIMIT_GB, PERIODS


def _cap_memory():
    lim = MEMORY_LIMIT_GB * 1024 ** 3
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))


def compact(stats, strategy):
    s = stats["strategy"][strategy]
    daily = defaultdict(float)
    for t in s.get("trades", []):
        daily[str(t["close_date"])[:10]] += float(t["profit_abs"])
    keys = ["total_trades", "profit_total", "profit_total_abs", "wins", "losses", "max_drawdown_account",
            "sharpe", "sortino", "calmar", "profit_factor", "market_change", "holding_avg", "timeframe",
            "backtest_start", "backtest_end", "stoploss", "trailing_stop",
            "trade_count_long", "trade_count_short", "profit_total_long", "profit_total_short"]
    out = {k: s.get(k) for k in keys}
    out["exit_reasons"] = {r.get("key", r.get("exit_reason")): r.get("trades") for r in s.get("exit_reason_summary", [])}
    out["daily_pnl"] = dict(sorted(daily.items()))
    return out


def run_one(strategy, period, timerange, cfg, pool, tmp):
    from freqtrade.data.btanalysis import load_backtest_stats
    d = tmp / f"{strategy}_{period}"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    cmd = [sys.executable, "-m", "lab.ft_run", "backtesting", "-c", cfg, "--strategy", strategy, "--strategy-path", pool,
           "--timerange", timerange, "--fee", str(FEE), "--export", "trades", "--export-directory", str(d),
           "--cache", "none"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=BACKTEST_TIMEOUT, preexec_fn=_cap_memory)
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "secs": BACKTEST_TIMEOUT}
    secs = round(time.time() - t0, 1)
    if p.returncode != 0:
        if "MemoryError" in p.stderr or "Cannot allocate memory" in p.stderr or p.returncode in (-9, 137):
            return {"error": f"memory: needed more than {MEMORY_LIMIT_GB} GB", "secs": secs}
        err = [l for l in (p.stderr + p.stdout).splitlines() if "Error" in l or "Exception" in l or "error" in l]
        return {"error": (err[-1] if err else (p.stderr or p.stdout)[-300:])[-400:], "secs": secs}
    try:
        res = compact(load_backtest_stats(d), strategy)
    except Exception as e:
        tail = " / ".join(l.split(" - ")[-1] for l in (p.stdout + p.stderr).splitlines()[-6:])
        return {"error": f"no result: {str(e)[:80]} | {tail}"[:600], "secs": secs}
    res["secs"] = secs
    shutil.rmtree(d, ignore_errors=True)
    return res


def main(runnable, shard, shards, cfg, pool, outdir):
    names = sorted(json.load(open(runnable)))
    mine = [n for i, n in enumerate(names) if i % int(shards) == int(shard)]
    out, tmp = Path(outdir), Path("/tmp/bt")
    out.mkdir(parents=True, exist_ok=True)
    print(f"shard {shard}/{shards}: {len(mine)} strategies", flush=True)
    for n in mine:
        rec = {"strategy": n}
        for period, tr in PERIODS.items():
            rec[period] = run_one(n, period, tr, cfg, pool, tmp)
        json.dump(rec, open(out / f"{n}.json", "w"))
        summary = " | ".join(f"{p}: " + (r["error"][:400] if "error" in r else
                             f"{r['total_trades']} trades {r['profit_total'] * 100:+.1f}%") for p, r in
                             ((p, rec[p]) for p in PERIODS))
        print(f"{n}: {summary}", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:7])
