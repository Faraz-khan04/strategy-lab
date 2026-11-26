# strategy-lab

Every public Freqtrade strategy we could find (~580 unique, from 7 GitHub collections) put through **one honest test**.

Most "this bot made X%" claims are a single strategy, on hand-picked dates, without fees, picked after the fact
from many that failed. This lab does the opposite:

1. **Collect** strategies from pinned commits of public repos (`sources.txt`), remove copies (same code ≠ new strategy).
2. **Vet the code without running it** (`lab/vet.py`): strategies that call the network, run shell commands or use `eval` are dropped.
3. **Same test for all**: 10 large coins, Binance spot data, 0.1% fees, $1,000 per trade, max 5 open trades.
4. **Two periods**: the leaders are picked on 2023–2024 and must hold up on 2025–Oct 2026.
5. **Luck adjustment**: with hundreds of tries, some look great by chance. The deflated Sharpe ratio
   (Bailey & López de Prado) says which leaders beat the best result expected from pure luck.
6. **Cheat check**: Freqtrade's look-ahead analysis on the leaders, with four deliberately cheating strategies as controls.

All rules are fixed in `lab/settings.py` before results are seen. The result lands in `report.md` on the
**`results`** branch.

## Run

Actions → **lab** → Run workflow (`limit` = 10 for a quick smoke test, 0 for everything).
Third-party code only ever runs in read-only jobs with no secrets.

Research only. Not financial advice. Third-party strategies are downloaded at run time and run unmodified;
their licences stay with their authors.
