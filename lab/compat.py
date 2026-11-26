"""Mechanical fixes for imports and aliases that newer numpy/pandas/Freqtrade removed.
Each one is a pure rename: the trading logic is untouched. Strategies that needed one are listed in the report."""
import re

FIXES = [
    (r"^from numpy\.lib import math\b.*$", "import math", re.M),
    (r"^from freqtrade\.state import RunMode\s*$", "from freqtrade.enums import RunMode", re.M),
    (r"\bnp\.NaN\b", "np.nan", 0),
    (r"\bnumpy\.NaN\b", "numpy.nan", 0),
    (r"\bnp\.NINF\b", "(-np.inf)", 0),
    (r"\bnp\.Inf\b", "np.inf", 0),
    (r"\.fillna\(\s*method\s*=\s*['\"](?:ffill|pad)['\"]\s*\)", ".ffill()", 0),
    (r"\.fillna\(\s*method\s*=\s*['\"](?:bfill|backfill)['\"]\s*\)", ".bfill()", 0),
]


def patch(code):
    applied = []
    for pat, rep, flags in FIXES:
        new, n = re.subn(pat, rep, code, flags=flags)
        if n:
            applied.append(f"{pat} x{n}")
            code = new
    return code, applied
