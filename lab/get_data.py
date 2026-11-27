"""Download Binance candles from the public archive (data.binance.vision) into Freqtrade's feather format.
Spot mode: spot candles. Futures mode: USDT-M futures candles, 1h mark-price candles and the real funding rates.
Usage: python -m lab.get_data <datadir>"""
import concurrent.futures as cf
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

from .settings import DATA_FROM, DATA_TO, MODE, PAIRS, QUOTE, TIMEFRAMES

BASE = "https://data.binance.vision/data/"
URL = {
    "spot": BASE + "spot/monthly/klines/{s}/{tf}/{s}-{tf}-{m}.zip",
    "futures": BASE + "futures/um/monthly/klines/{s}/{tf}/{s}-{tf}-{m}.zip",
    "mark": BASE + "futures/um/monthly/markPriceKlines/{s}/{tf}/{s}-{tf}-{m}.zip",
    "funding_rate": BASE + "futures/um/monthly/fundingRate/{s}/{s}-fundingRate-{m}.zip",
}
MARK_TF = FUNDING_TF = "1h"                       # what Freqtrade expects for the market-metadata exchange (OKX)


def months(a, b):
    return [str(p) for p in pd.period_range(a, b, freq="M")]


def download(url):
    for attempt in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "strategy-lab"}), timeout=60).read()
        except Exception as e:
            if "404" in str(e):
                return None
            if attempt == 3:
                raise


def fetch_funding(sym, m):
    """Funding settlements -> Freqtrade's funding_rate layout: date, funding_rate."""
    raw = download(URL["funding_rate"].format(s=sym, m=m))
    if raw is None:
        return None
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        text = z.read(z.namelist()[0])
    df = pd.read_csv(io.BytesIO(text))
    if not str(df.columns[0]).startswith("calc"):  # no header row
        df = pd.read_csv(io.BytesIO(text), header=None)
        df.columns = ["calc_time", "funding_interval_hours", "last_funding_rate"][: df.shape[1]]
    ts = df["calc_time"].astype("int64")
    unit = "us" if ts.iloc[0] > 1e14 else "ms"
    date = pd.to_datetime(ts, unit=unit, utc=True).dt.floor("h")   # settlement stamps are a few ms off the hour
    return pd.DataFrame({"date": date, "funding_rate": df["last_funding_rate"].astype(float)})


def fetch(sym, tf, m, kind=None):
    url = URL[kind or MODE].format(s=sym, tf=tf, m=m)
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "strategy-lab"}), timeout=60).read()
            break
        except Exception as e:
            if "404" in str(e):
                return None
            if attempt == 3:
                raise
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        df = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=range(6))
    if not str(df.iloc[0, 0]).isdigit():          # some files carry a header row
        df = df.iloc[1:]
    df = df.astype(float)
    df.columns = ["ts", "open", "high", "low", "close", "volume"]
    unit = "us" if df["ts"].iloc[0] > 1e14 else "ms"   # Binance moved spot files to microseconds in 2025
    df["date"] = pd.to_datetime(df["ts"].astype("int64"), unit=unit, utc=True)
    return df[["date", "open", "high", "low", "close", "volume"]]


def main(datadir):
    out = Path(datadir) / ("futures" if MODE == "futures" else "")
    out.mkdir(parents=True, exist_ok=True)
    ms = months(DATA_FROM, DATA_TO)
    kind0 = MODE
    jobs = [(p + QUOTE, tf, m, kind0) for p in PAIRS for tf in TIMEFRAMES for m in ms]
    if MODE == "futures":
        jobs += [(p + QUOTE, MARK_TF, m, "mark") for p in PAIRS for m in ms]
        jobs += [(p + QUOTE, FUNDING_TF, m, "funding_rate") for p in PAIRS for m in ms]
    parts = {}

    def get(j):
        sym, tf, m, kind = j
        return fetch_funding(sym, m) if kind == "funding_rate" else fetch(sym, tf, m, kind)

    with cf.ThreadPoolExecutor(16) as ex:
        for (sym, tf, m, kind), df in zip(jobs, ex.map(get, jobs)):
            if df is not None:
                parts.setdefault((sym, tf, kind), []).append(df)
    for (sym, tf, kind), dfs in sorted(parts.items()):
        df = pd.concat(dfs).drop_duplicates("date").sort_values("date").reset_index(drop=True)
        base = sym[:-len(QUOTE)]
        if MODE == "futures":
            name = f"{base}_{QUOTE}_{QUOTE}-{tf}-{kind}.feather"      # e.g. BTC_USDT_USDT-5m-futures.feather
        else:
            name = f"{base}_{QUOTE}-{tf}.feather"
        df.to_feather(out / name)
        step = pd.Timedelta(tf.replace("m", "min").replace("h", "h").replace("d", "D"))
        if kind == "funding_rate":
            step = pd.Timedelta("8h")
        gaps = int((df["date"].diff() > step).sum())
        print(f"{name:24s} {len(df):8d} candles {df['date'].iloc[0]:%Y-%m-%d} -> {df['date'].iloc[-1]:%Y-%m-%d} gaps={gaps}")
    need = [(p + QUOTE, tf, MODE) for p in PAIRS for tf in TIMEFRAMES]
    if MODE == "futures":
        need += [(p + QUOTE, MARK_TF, k) for p in PAIRS for k in ("mark", "funding_rate")]
    missing = [n for n in need if n not in parts]
    if missing:
        sys.exit(f"missing series: {missing}")


if __name__ == "__main__":
    main(sys.argv[1])
