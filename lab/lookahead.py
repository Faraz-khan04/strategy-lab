"""Freqtrade's look-ahead check on the selection leaders and the deliberately-cheating controls.
Usage: python -m lab.lookahead <targets.json> <config.json> <pool> <out.json>"""
import csv
import json
import subprocess
import sys
from pathlib import Path

TIMERANGE = "20240101-20240401"


def main(targets, cfg, pool, out):
    res = {}
    for name in json.load(open(targets)):
        csv_path = Path(f"/tmp/la_{name}.csv")
        cmd = [sys.executable, "-m", "lab.ft_run", "lookahead-analysis", "-c", cfg, "--strategy", name, "--strategy-path", pool,
               "--timerange", TIMERANGE, "--lookahead-analysis-exportfilename", str(csv_path)]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            rows = list(csv.DictReader(open(csv_path))) if csv_path.exists() else []
            if not rows:
                res[name] = "not checked"
            else:
                res[name] = "CHEATS (look-ahead bias)" if any(r.get("has_bias", "").lower() == "true" for r in rows) else "clean"
        except subprocess.TimeoutExpired:
            res[name] = "check timed out"
        print(name, res[name], flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:5])
