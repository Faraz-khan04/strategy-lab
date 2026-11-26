"""Static vetting of strategy files: reads the code, never runs it.
Flags: legacy API (won't load in current Freqtrade), extra packages, and risky calls (network, shell, eval)."""
import ast, collections, json, os, sys

pool = sys.argv[1]
STD_OK = {"freqtrade", "talib", "numpy", "pandas", "technical", "datetime", "typing", "functools", "math", "logging",
          "pandas_ta", "scipy", "warnings", "decimal", "enum", "time", "statistics", "collections", "itertools", "abc", "copy", "array"}
RISKY_MODULES = {"requests", "urllib", "socket", "subprocess", "http", "aiohttp", "websocket", "websockets", "paramiko",
                 "ftplib", "smtplib", "ctypes", "pickle", "marshal", "shutil", "telegram", "httpx"}
RISKY_CALLS = {"eval", "exec", "compile", "__import__", "system", "popen", "b64decode", "remove", "rmtree", "unlink"}

rows, cnt = [], collections.Counter()
for f in sorted(os.listdir(pool)):
    if not f.endswith(".py"):
        continue
    code = open(os.path.join(pool, f), encoding="utf-8", errors="replace").read()
    tree = ast.parse(code)
    mods, calls, funcs = set(), set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module.split(".")[0])
        elif isinstance(n, ast.Call):
            fn = n.func
            calls.add(getattr(fn, "id", None) or getattr(fn, "attr", None))
        elif isinstance(n, ast.FunctionDef):
            funcs.add(n.name)
    legacy = "populate_buy_trend" in funcs and "populate_entry_trend" not in funcs
    extra = sorted(mods - STD_OK - RISKY_MODULES - {"__future__", "os", "sys", "json", "pathlib", "re", "random", "inspect"})
    risky = sorted((mods & RISKY_MODULES) | (calls & RISKY_CALLS) | ({"os"} & mods and {"os (file/env access)"} or set()))
    r = {"strategy": f[:-3], "legacy_api": legacy, "extra_packages": extra, "risky": risky,
         "has_stoploss": "stoploss" in code, "lines": code.count("\n")}
    rows.append(r)
    cnt["legacy"] += legacy
    cnt["extra_pkgs"] += bool(extra)
    cnt["risky"] += bool(risky)
    cnt["modern_clean"] += (not legacy and not extra and not risky)
json.dump(rows, open(os.path.join(pool, "vetting.json"), "w"), indent=1)
print(len(rows), dict(cnt))
print("extra packages seen:", collections.Counter(p for r in rows for p in r["extra_packages"]).most_common(12))
print("risky findings:", collections.Counter(x for r in rows for x in r["risky"]).most_common(12))
