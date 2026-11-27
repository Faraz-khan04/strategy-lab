"""Build the strategy pool: fetch every source at its pinned commit, keep one copy of each strategy,
vet the code without running it, and drop what is risky or needs a package we don't install.
Usage: python -m lab.prepare <workdir>   -> <workdir>/pool/*.py, <workdir>/candidates.json"""
import json
import re
import subprocess

from .compat import patch
from .settings import MODE, SOURCES_FILE

SHORTS = re.compile(r"can_short\s*(?::\s*bool)?\s*=\s*True")
import sys
from pathlib import Path

INSTALLABLE = {"cachetools", "rapidjson", "arrow", "skopt", "finta", "ta", "sklearn", "sqlalchemy", "tabulate"}


def sh(*a, cwd=None):
    subprocess.run(a, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main(work):
    work = Path(work)
    src = work / "sources"
    src.mkdir(parents=True, exist_ok=True)
    for line in Path(SOURCES_FILE).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        url, sha = line.split()
        d = src / url.rstrip("/").split("github.com/")[1].replace("/", "_")
        if not d.exists():
            d.mkdir()
            sh("git", "init", "-q", cwd=d)
            sh("git", "fetch", "-q", "--depth", "1", url, sha, cwd=d)
            sh("git", "checkout", "-q", "FETCH_HEAD", cwd=d)
    pool = work / "pool"
    subprocess.run([sys.executable, "-I", "lab/collect.py", str(src), str(pool)], check=True)
    subprocess.run([sys.executable, "-I", "lab/vet.py", str(pool)], check=True)
    vet = json.loads((pool / "vetting.json").read_text())
    manifest = {m["strategy"]: m["source"] for m in json.loads((pool / "manifest.json").read_text())}
    keep, dropped = [], []
    for r in vet:
        why = None
        code = (pool / f"{r['strategy']}.py").read_text(encoding="utf-8", errors="replace")
        if MODE == "futures" and not SHORTS.search(code):
            (pool / f"{r['strategy']}.py").unlink()      # long-only: not part of the futures test
            continue
        if "freqai" in code.lower():
            why = "needs FreqAI (machine-learning training)"
        elif r["risky"]:
            why = "risky code: " + ", ".join(r["risky"])
        elif set(r["extra_packages"]) - INSTALLABLE:
            why = "needs " + ", ".join(sorted(set(r["extra_packages"]) - INSTALLABLE))
        if why:
            dropped.append({"strategy": r["strategy"], "source": manifest.get(r["strategy"]), "reason": why})
            (pool / f"{r['strategy']}.py").unlink()
        else:
            f = pool / f"{r['strategy']}.py"
            code, applied = patch(f.read_text(encoding="utf-8"))
            if applied:
                f.write_text(code, encoding="utf-8")
            keep.append({"strategy": r["strategy"], "source": manifest.get(r["strategy"]), "legacy_api": r["legacy_api"],
                         "compat_fixes": applied})
    json.dump({"keep": keep, "dropped": dropped}, open(work / "candidates.json", "w"), indent=1)
    print(f"candidates: {len(keep)} kept, {len(dropped)} dropped")


if __name__ == "__main__":
    main(sys.argv[1])
