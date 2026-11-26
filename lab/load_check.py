"""Which pool strategies import cleanly in this Freqtrade version (third-party code runs here: CI only).
Usage: python -m lab.load_check <pool> <work>  -> work/load_status.json, work/runnable.json"""
import json
import logging
import sys
from pathlib import Path

import freqtrade
from freqtrade.resolvers import StrategyResolver


class Catch(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.msgs = []

    def emit(self, record):
        self.msgs.append(record.getMessage())


def main(pool, work):
    catch = Catch()
    logging.getLogger("freqtrade").addHandler(catch)
    pool_dir = Path(pool).resolve()
    objs = StrategyResolver.search_all_objects({"strategy_path": str(pool_dir), "user_data_dir": Path("user_data")}, True)
    status = {"_version": freqtrade.__version__}
    for o in objs:
        loc = Path(o["location"]).resolve()
        if loc.parent != pool_dir:          # freqtrade's own templates are searched too: not ours
            continue
        stem = loc.stem
        if o["class"] is not None and o["name"] == stem:
            status[stem] = "OK"                       # a file may hold helper classes too: one match is enough
        elif status.get(stem) != "OK":
            status[stem] = "LOAD FAILED" if o["class"] is None else "NAME MISMATCH"
    for stem, v in list(status.items()):
        if v == "LOAD FAILED":
            hit = [m for m in catch.msgs if f"{stem}.py" in m or f"/{stem}" in m]
            status[stem] = "LOAD FAILED: " + (hit[-1].split(" due to ")[-1][:160] if hit else "unknown")
    runnable = sorted(k for k, v in status.items() if v == "OK" and k != "_version")
    json.dump(status, open(Path(work) / "load_status.json", "w"), indent=1)
    json.dump(runnable, open(Path(work) / "runnable.json", "w"))
    print(f"{len(runnable)} of {len(status) - 1} strategies load")


if __name__ == "__main__":
    main(*sys.argv[1:3])
