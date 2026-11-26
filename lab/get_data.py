"""Download Binance spot candles from the public archive (data.binance.vision) into Freqtrade's feather format.
Usage: python -m lab.get_data <datadir>"""
import concurrent.futures as cf
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

from .settings import DATA_FROM, DATA_TO, PAIRS, QUOTE, TIMEFRAMES

URL = "https://data.binance.vision/data/spot/monthly/klines/{s}/{tf}/{s}-{tf}-{m}.zip"


def months(a, b):
    return [str(p) for p in pd.period_range(a, b, freq="M")]


def fetch(sym, tf, m):
    url = URL.format(s=sym, tf=tf, m=m)
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
    out = Path(datadir)
    out.mkdir(parents=True, exist_ok=True)
    ms = months(DATA_FROM, DATA_TO)
    jobs = [(p + QUOTE, tf, m) for p in PAIRS for tf in TIMEFRAMES for m in ms]
    parts = {}
    with cf.ThreadPoolExecutor(16) as ex:
        for (sym, tf, m), df in zip(jobs, ex.map(lambda j: fetch(*j), jobs)):
            if df is not None:
                parts.setdefault((sym, tf), []).append(df)
    for (sym, tf), dfs in sorted(parts.items()):
        df = pd.concat(dfs).drop_duplicates("date").sort_values("date").reset_index(drop=True)
        name = f"{sym[:-len(QUOTE)]}_{QUOTE}-{tf}.feather"
        df.to_feather(out / name)
        step = pd.Timedelta(tf.replace("m", "min").replace("h", "h").replace("d", "D"))
        gaps = int((df["date"].diff() > step).sum())
        print(f"{name:24s} {len(df):8d} candles {df['date'].iloc[0]:%Y-%m-%d} -> {df['date'].iloc[-1]:%Y-%m-%d} gaps={gaps}")
    missing = [(p, tf) for p in PAIRS for tf in TIMEFRAMES if (p + QUOTE, tf) not in parts]
    if missing:
        sys.exit(f"missing series: {missing}")


if __name__ == "__main__":
    main(sys.argv[1])
