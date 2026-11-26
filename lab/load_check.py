"""Which pool strategies import cleanly in this Freqtrade version (third-party code runs here: CI only).
Usage: python -m lab.load_check <pool> <work>  -> work/load_status.json, work/runnable.json"""
import json
import sys
from pathlib import Path

import freqtrade
from freqtrade.resolvers import StrategyResolver


def main(pool, work):
    objs = StrategyResolver.search_all_objects({"strategy_path": pool, "user_data_dir": "user_data"}, True)
    status = {"_version": freqtrade.__version__}
    for o in objs:
        stem = Path(o["location"]).stem
        status[stem] = "OK" if o["class"] is not None and o["name"] == stem else ("LOAD FAILED" if o["class"] is None else "NAME MISMATCH")
    runnable = sorted(k for k, v in status.items() if v == "OK")
    json.dump(status, open(Path(work) / "load_status.json", "w"), indent=1)
    json.dump(runnable, open(Path(work) / "runnable.json", "w"))
    print(f"{len(runnable)} of {len(status) - 1} strategies load")


if __name__ == "__main__":
    main(*sys.argv[1:3])
