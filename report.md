# Strategy lab — every public Freqtrade strategy, one honest test

_Generated 2026-11-26 16:56 UTC._

## The test

- 10 coins vs USDT (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, LINK, LTC), Binance spot candles from data.binance.vision.
- Fees 0.1% per side, $1,000 per trade, at most 5 open trades, $10,000 wallet. Each strategy keeps its own timeframe, ROI table and stoploss.
- **Selection period** 20230101-20250101 — the leaders are picked here. **Confirmation period** 20250101-20261101 — they have to hold up here.
- A strategy needs ≥30 trades in a period to be judged. These rules were fixed before any result was seen.

## Funnel

| step | strategies |
|---|---|
| unique strategies after removing copies | 586 |
| dropped by code vetting (risky code or unavailable package) | 20 |
| load in Freqtrade 2026.10 | 554 (99 needed a one-line import/alias fix, logic untouched) |
| backtested (after merging 52 that trade identically to another) | 502 |
| backtested without error in both periods | 351 |
| ≥30 trades in the selection period | 322 |
| ≥30 trades in both periods | 300 |

## What the market did

| period | buy & hold, 10 coins equal weight | BTC |
|---|---|---|
| select | +425.7% | +463.1% |
| confirm | -47.5% | -18.0% |

## The whole field

- Selection period: **52%** of strategies were profitable after fees; median return +1.2%.
- Confirmation period: **16%** profitable; median return -43.1%.
- Does selection-period rank predict confirmation-period rank? Spearman correlation of daily Sharpe: **+0.91** (0 = no relation, 1 = perfect).
- Luck bar: with 322 strategies and no skill at all, the best daily Sharpe expected by chance is 0.516 (≈9.86 annualised). **0** strategies cleared it with ≥95% confidence.

## The top 20 of the selection period, followed into confirmation

| strategy | source | select return | select Sharpe (ann.) | beyond luck | confirm trades | confirm return | confirm Sharpe | look-ahead |
|---|---|---|---|---|---|---|---|---|
| BBRSIv2 | keithorange | +49.1% | 9.46 | 18% | 164 | -9.9% | -0.23 | clean |
| LookaheadStrategy | keithorange | +288.2% | 9.06 | 4% | 445 | +131.6% | 7.81 | CHEATS (look-ahead bias) |
| ichiV1 | keithorange | +337.4% | 8.45 | 1% | 1966 | +188.2% | 6.04 | CHEATS (look-ahead bias) |
| Hacklemore3 | keithorange | +41.8% | 6.07 | 0% | 77 | -22.1% | -0.49 | clean |
| Ichimoku_v12 | keithorange | +71.9% | 5.76 | 0% | 44 | -13.9% | -0.30 | clean |
| ONUR | keithorange | +53.8% | 5.42 | 0% | 57 | -17.3% | -0.39 | clean |
| Hacklemore2 | keithorange | +26.9% | 5.31 | 0% | 190 | -17.8% | -0.46 | clean |
| StrategyScalpingFast | keithorange | +51.7% | 4.97 | 1% | 401 | -37.8% | -0.94 | clean |
| Supertrend__9fb282 | werkkrew | +49.2% | 4.88 | 0% | 205 | -18.4% | -0.45 | clean |
| Babico_SMA5xBBmid | keithorange | +56.3% | 4.71 | 0% | 106 | -17.8% | -0.46 | clean |
| ElliotV4 | keithorange | +24.7% | 4.20 | 0% | 53 | -15.6% | -0.56 | clean |
| ElliotV5HOMod2 | keithorange | +17.9% | 4.05 | 0% | 20 | -4.4% | -0.39 | clean |
| EI3v2_tag_cofi_green | keithorange | +55.5% | 3.98 | 0% | 333 | +18.6% | 1.65 | clean |
| NostalgiaForInfinityX6 | iterativv_NostalgiaForInfinity | +25.8% | 3.76 | 0% | 57 | +18.2% | 1.97 | CHEATS (look-ahead bias) |
| redditMA | keithorange | +34.5% | 3.57 | 0% | 637 | -25.4% | -0.87 | clean |
| NFINextMultiOffsetAndHO2 | keithorange | +15.0% | 3.55 | 0% | 102 | +2.3% | 0.56 | clean |
| Nostalgia | keithorange | +18.4% | 3.46 | 0% | 139 | +1.6% | 0.35 | clean |
| Slowbro | keithorange | +28.9% | 3.44 | 0% | 18 | -12.8% | -0.33 | clean |
| Combined_NFIv7_SMA | keithorange | +22.9% | 3.41 | 0% | 133 | +0.8% | 0.16 | clean |
| Combined_NFIv6_SMA | keithorange | +23.3% | 3.40 | 0% | 136 | -0.5% | -0.11 | clean |

**7 of 20** stayed profitable in confirmation; **20** beat buy & hold (-47.5%).

## Controls (strategies written to cheat by peeking at the future)

| strategy | select return | look-ahead check |
|---|---|---|
| DevilStra__566d66 | — | not checked |
| GodStraNew__d11747 | +23.9% | CHEATS (look-ahead bias) |
| Zeus | +21.2% | CHEATS (look-ahead bias) |
| wtc__985d94 | — | CHEATS (look-ahead bias) |

If the look-ahead check does not flag these, the harness is not catching cheaters.

## Strategies that would not load

| reason | strategies |
|---|---|
| LOAD FAILED: 'name 'Schism' is not defined' | 5 |
| LOAD FAILED: 'name 'Tuple' is not defined' | 2 |
| LOAD FAILED: 'name 'Schism6' is not defined' | 1 |
| LOAD FAILED: 'No module named 'technical.tradingview'' | 1 |
| LOAD FAILED: 'name 'Cluc4werk' is not defined' | 1 |
| LOAD FAILED: 'name 'ClucHAnix' is not defined' | 1 |
| LOAD FAILED: 'name 'BB_RPB_TSL_SMA_Tranz_TB' is not defined' | 1 |

## Backtest failures

| reason | strategies |
|---|---|
| no result | 53 |
| TypeError | 37 |
| numpy.exceptions.DTypePromotionError | 27 |
| timeout | 11 |
| ImportError | 6 |
| yze ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ | 4 |
| KeyError | 3 |
| 00 | 3 |
| 2026-11-26 15 | 2 |
| memory | 2 |
| 2026-11-26 14 | 1 |
|  | 1 |

Research only, not financial advice. Third-party strategies were run unmodified; sources and commits are in sources.txt.