"""Turn every backtest into one honest report.
Usage: python -m lab.aggregate <results_dir> <work_dir> <datadir> [lookahead.json]  -> report.md, results.csv"""
import csv
import datetime as dt
import json
import math
import statistics as st
import sys
from pathlib import Path

from .settings import DSR_PASS, FEE, MAX_OPEN, MIN_TRADES, PAIRS, PERIODS, QUOTE, STAKE, TOP_PICKS, WALLET

N01 = st.NormalDist()
EULER = 0.5772156649


def period_days(tr):
    a, b = tr.split("-")
    d0, d1 = dt.date.fromisoformat(f"{a[:4]}-{a[4:6]}-{a[6:]}"), dt.date.fromisoformat(f"{b[:4]}-{b[4:6]}-{b[6:]}")
    return [(d0 + dt.timedelta(i)).isoformat() for i in range((d1 - d0).days)]


def daily_stats(r, tr):
    """Sharpe per day, skew, kurtosis of the daily return series (days without a closed trade count as 0)."""
    days = period_days(tr)
    x = [r["daily_pnl"].get(d, 0.0) / WALLET for d in days]
    m, sd = st.fmean(x), st.pstdev(x)
    if sd == 0:
        return None
    sr = m / sd
    skew = st.fmean([((v - m) / sd) ** 3 for v in x])
    kurt = st.fmean([((v - m) / sd) ** 4 for v in x])
    return {"sr": sr, "sr_ann": sr * math.sqrt(365), "skew": skew, "kurt": kurt, "T": len(x)}


def deflated(sr, skew, kurt, T, sr0):
    den = 1 - skew * sr + (kurt - 1) / 4 * sr * sr
    if den <= 0:
        return 0.0
    return N01.cdf((sr - sr0) * math.sqrt(T - 1) / math.sqrt(den))


def expected_max_sr(srs):
    """The best Sharpe you'd expect from len(srs) strategies with no skill at all (False Strategy Theorem)."""
    n = len(srs)
    if n < 2:
        return 0.0
    v = st.pvariance(srs)
    return math.sqrt(v) * ((1 - EULER) * N01.inv_cdf(1 - 1 / n) + EULER * N01.inv_cdf(1 - 1 / (n * math.e)))


def spearman(a, b):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    ra, rb = ranks(a), ranks(b)
    return st.correlation(ra, rb) if len(a) > 2 else None


def buy_and_hold(datadir, tr):
    import pandas as pd
    a, b = tr.split("-")
    t0, t1 = pd.Timestamp(a, tz="UTC"), pd.Timestamp(b, tz="UTC") - pd.Timedelta(days=1)
    out = {}
    for p in PAIRS:
        df = pd.read_feather(Path(datadir) / f"{p}_{QUOTE}-1d.feather").set_index("date")["close"]
        out[p] = float(df.asof(t1) / df.asof(t0) - 1)
    return st.fmean(out.values()), out


def pct(x, d=1):
    return "—" if x is None else f"{x * 100:+.{d}f}%"


def main(results_dir, work, datadir, lookahead=None):
    work = Path(work)
    cand = json.loads((work / "candidates.json").read_text())
    loadable = json.loads((work / "load_status.json").read_text())
    la = json.loads(Path(lookahead).read_text()) if lookahead and Path(lookahead).exists() else {}
    recs = {p.stem: json.loads(p.read_text()) for p in Path(results_dir).glob("*.json")}
    sources = {c["strategy"]: c["source"] for c in cand["keep"]}
    rows = []
    for name, rec in recs.items():
        row = {"strategy": name, "source": (sources.get(name) or "").split("/")[0]}
        for per, tr in PERIODS.items():
            r = rec.get(per, {})
            if "error" in r:
                row[f"{per}_error"] = r["error"][:120]
                continue
            row[f"{per}_trades"] = r["total_trades"]
            row[f"{per}_return"] = r["profit_total"]
            row[f"{per}_maxdd"] = r["max_drawdown_account"]
            ds = daily_stats(r, tr) if r["total_trades"] else None
            if ds:
                row.update({f"{per}_{k}": v for k, v in ds.items()})
        rows.append(row)

    ok = lambda r, per: r.get(f"{per}_trades", 0) >= MIN_TRADES and f"{per}_sr" in r
    sel = [r for r in rows if ok(r, "select")]
    sr0 = expected_max_sr([r["select_sr"] for r in sel])
    for r in sel:
        r["select_dsr"] = deflated(r["select_sr"], r["select_skew"], r["select_kurt"], r["select_T"], sr0)
    both = [r for r in sel if ok(r, "confirm")]
    rho = spearman([r["select_sr"] for r in both], [r["confirm_sr"] for r in both]) if len(both) > 2 else None
    bh = {per: buy_and_hold(datadir, tr) for per, tr in PERIODS.items()}
    picks = sorted(sel, key=lambda r: -r["select_sr"])[:TOP_PICKS]
    dsr_pass = [r for r in sel if r["select_dsr"] >= DSR_PASS]
    errors = [r for r in rows if "select_error" in r or "confirm_error" in r]

    def prof(rs, per):
        v = [r[f"{per}_return"] for r in rs if f"{per}_return" in r]
        return (sum(x > 0 for x in v) / len(v), st.median(v)) if v else (None, None)

    L = ["# Strategy lab — every public Freqtrade strategy, one honest test", "",
         f"_Generated {dt.datetime.now(dt.UTC):%Y-%m-%d %H:%M} UTC._", "",
         "## The test", "",
         f"- {len(PAIRS)} coins vs {QUOTE} ({', '.join(PAIRS)}), Binance spot candles from data.binance.vision.",
         f"- Fees {FEE:.1%} per side, ${STAKE:,} per trade, at most {MAX_OPEN} open trades, ${WALLET:,} wallet. Each strategy keeps its own timeframe, ROI table and stoploss.",
         f"- **Selection period** {PERIODS['select']} — the leaders are picked here. **Confirmation period** {PERIODS['confirm']} — they have to hold up here.",
         f"- A strategy needs ≥{MIN_TRADES} trades in a period to be judged. These rules were fixed before any result was seen.", "",
         "## Funnel", "",
         f"| step | strategies |", "|---|---|",
         f"| unique strategies after removing copies | {len(cand['keep']) + len(cand['dropped'])} |",
         f"| dropped by code vetting (risky code or unavailable package) | {len(cand['dropped'])} |",
         f"| load in Freqtrade {loadable.get('_version', '')} | {sum(1 for k, v in loadable.items() if v == 'OK')} |",
         f"| backtested without error in both periods | {len(rows) - len(errors)} |",
         f"| ≥{MIN_TRADES} trades in the selection period | {len(sel)} |",
         f"| ≥{MIN_TRADES} trades in both periods | {len(both)} |", "",
         "## What the market did", "",
         "| period | buy & hold, 10 coins equal weight | BTC |", "|---|---|---|"]
    for per in PERIODS:
        L.append(f"| {per} | {pct(bh[per][0])} | {pct(bh[per][1]['BTC'])} |")
    p_sel, m_sel = prof(sel, "select")
    p_both, m_both = prof(both, "confirm")
    L += ["", "## The whole field", "",
          f"- Selection period: **{p_sel:.0%}** of strategies were profitable after fees; median return {pct(m_sel)}." if p_sel is not None else "",
          f"- Confirmation period: **{p_both:.0%}** profitable; median return {pct(m_both)}." if p_both is not None else "",
          f"- Does selection-period rank predict confirmation-period rank? Spearman correlation of daily Sharpe: **{rho:+.2f}** "
          "(0 = no relation, 1 = perfect)." if rho is not None else "",
          f"- Luck bar: with {len(sel)} strategies and no skill at all, the best daily Sharpe expected by chance is {sr0:.3f} "
          f"(≈{sr0 * math.sqrt(365):.2f} annualised). **{len(dsr_pass)}** strategies cleared it with ≥{DSR_PASS:.0%} confidence.", "",
          f"## The top {TOP_PICKS} of the selection period, followed into confirmation", "",
          "| strategy | source | select return | select Sharpe (ann.) | beyond luck | confirm trades | confirm return | confirm Sharpe | look-ahead |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in picks:
        lk = la.get(r["strategy"], "—")
        L.append(f"| {r['strategy']} | {r['source']} | {pct(r['select_return'])} | {r['select_sr_ann']:.2f} | {r['select_dsr']:.0%} | "
                 f"{r.get('confirm_trades', '—')} | {pct(r.get('confirm_return'))} | "
                 f"{r['confirm_sr_ann']:.2f} | {lk} |" if 'confirm_sr_ann' in r else
                 f"| {r['strategy']} | {r['source']} | {pct(r['select_return'])} | {r['select_sr_ann']:.2f} | {r['select_dsr']:.0%} | "
                 f"{r.get('confirm_trades', '—')} | {pct(r.get('confirm_return'))} | — | {lk} |")
    held = [r for r in picks if r.get("confirm_return", -1) > 0]
    beat = [r for r in picks if r.get("confirm_return", -1) > bh["confirm"][0]]
    L += ["", f"**{len(held)} of {len(picks)}** stayed profitable in confirmation; **{len(beat)}** beat buy & hold ({pct(bh['confirm'][0])}).", ""]
    if dsr_pass:
        L += ["## Strategies that cleared the luck bar", "", "| strategy | select return | beyond luck | confirm return | look-ahead |", "|---|---|---|---|---|"]
        for r in sorted(dsr_pass, key=lambda r: -r["select_dsr"]):
            L.append(f"| {r['strategy']} | {pct(r['select_return'])} | {r['select_dsr']:.0%} | {pct(r.get('confirm_return'))} | {la.get(r['strategy'], '—')} |")
        L.append("")
    ctrl = [n for n, s in sources.items() if "lookahead_bias" in (s or "")]
    if ctrl:
        L += ["## Controls (strategies written to cheat by peeking at the future)", "",
              "| strategy | select return | look-ahead check |", "|---|---|---|"]
        for n in ctrl:
            r = next((x for x in rows if x["strategy"] == n), {})
            L.append(f"| {n} | {pct(r.get('select_return'))} | {la.get(n, '—')} |")
        L += ["", "If the look-ahead check does not flag these, the harness is not catching cheaters.", ""]
    err_kinds = {}
    for r in errors:
        e = (r.get("select_error") or r.get("confirm_error") or "")
        k = "timeout" if e == "timeout" else e.split(":")[0][:60]
        err_kinds[k] = err_kinds.get(k, 0) + 1
    L += ["## Failures", "", "| reason | strategies |", "|---|---|"] + \
         [f"| {k} | {v} |" for k, v in sorted(err_kinds.items(), key=lambda x: -x[1])[:12]]
    L += ["", "Research only, not financial advice. Third-party strategies were run unmodified; sources and commits are in sources.txt."]
    Path("report.md").write_text("\n".join(l for l in L if l is not None), encoding="utf-8")
    cols = sorted({k for r in rows for k in r if k not in ("strategy", "source")})
    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["strategy", "source"] + cols)
        w.writeheader()
        w.writerows(rows)
    json.dump([r["strategy"] for r in picks] + [n for n in ctrl if n not in {r["strategy"] for r in picks}],
              open(work / "lookahead_targets.json", "w"))
    print("\n".join(L[:60]))


if __name__ == "__main__":
    main(*sys.argv[1:5])
