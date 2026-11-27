# Strategy lab — every public Freqtrade strategy that can short (USDT-M futures), one honest test

_Generated 2026-11-27 14:15 UTC._

## The test

- 10 coins vs USDT (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, LINK, LTC), Binance USDT-M perpetual futures candles from data.binance.vision, with Binance's real historical funding rates and mark prices.
- Fees 0.05% per side, $1,000 per trade, at most 5 open trades, $10,000 wallet. Each strategy keeps its own timeframe, ROI table and stoploss.
- **Leverage forced to 1x** for every strategy (isolated margin), whatever its author set, so the signals are judged rather than the leverage. Only strategies that can open shorts are tested.
- **Selection period** 20230101-20250101 — the leaders are picked here. **Confirmation period** 20250101-20261101 — they have to hold up here.
- A strategy needs ≥30 trades in a period to be judged. These rules were fixed before any result was seen.

## Funnel

| step | strategies |
|---|---|
| unique strategies after removing copies | 536 |
| dropped by code vetting (risky code or unavailable package) | 109 |
| load in Freqtrade 2026.10 | 393 (40 needed a one-line import/alias fix, logic untouched) |
| backtested (after merging 23 that trade identically to another) | 370 |
| backtested without error in both periods | 274 |
| ≥30 trades in the selection period | 242 |
| ≥30 trades in both periods | 238 |

## What the market did

| period | buy & hold, 10 coins equal weight | BTC |
|---|---|---|
| select | +425.9% | +463.2% |
| confirm | -47.5% | -18.0% |

## Longs vs shorts (all strategies with ≥30 trades)

| period | median return from longs | median return from shorts | strategies with a liquidation |
|---|---|---|---|
| select | +1.2% | -19.4% | 11 |
| confirm | -5.1% | -0.0% | 8 |

## The whole field

- Selection period: **35%** of strategies were profitable after fees; median return -12.3%.
- Confirmation period: **35%** profitable; median return -10.9%.
- Does selection-period rank predict confirmation-period rank? Spearman correlation of daily Sharpe: **+0.79** (0 = no relation, 1 = perfect).
- Luck bar: with 242 strategies and no skill at all, the best daily Sharpe expected by chance is 0.863 (≈16.50 annualised). **6** strategies cleared it with ≥95% confidence.

## The top 20 of the selection period, followed into confirmation

| strategy | source | select return | select Sharpe (ann.) | beyond luck | confirm trades | confirm return | confirm Sharpe | look-ahead | confirm: longs / shorts |
|---|---|---|---|---|---|---|---|---|---|
| SlopeV8 | remiotore_ccxt-freqtrade | +6571.0% | 37.67 | 100% | 96797 | +6393.5% | 36.03 | CHEATS (look-ahead bias) | +3214.8% / +3178.7% |
| MSlopeV8 | remiotore_ccxt-freqtrade | +6571.0% | 37.67 | 100% | 98843 | +6275.0% | 35.79 | CHEATS (look-ahead bias) | +3153.2% / +3121.8% |
| DivergenceStrategy | remiotore_ccxt-freqtrade | +1399.3% | 24.68 | 100% | 5886 | +1490.7% | 22.22 | CHEATS (look-ahead bias) | +742.1% / +748.6% |
| mk1 | RoboticAutomations_freqtradestrategies | +1088.9% | 24.47 | 100% | 37485 | +947.7% | 24.44 | CHEATS (look-ahead bias) | +488.1% / +459.7% |
| IchiVwapAdx | RoboticAutomations_freqtradestrategies | +522.4% | 20.15 | 100% | 19899 | +438.4% | 18.07 | CHEATS (look-ahead bias) | +214.7% / +223.7% |
| NOTankAi_15_ali | TheoBrigitte_freqtrade | +1161.3% | 19.48 | 100% | 10154 | +781.8% | 18.91 | CHEATS (look-ahead bias) | +421.5% / +360.3% |
| LSV1 | remiotore_ccxt-freqtrade | +1059.3% | 15.00 | 5% | 50796 | +839.6% | 14.44 | CHEATS (look-ahead bias) | +400.1% / +439.5% |
| LSV2 | remiotore_ccxt-freqtrade | +1241.9% | 14.44 | 1% | 70404 | +945.9% | 13.18 | CHEATS (look-ahead bias) | +442.2% / +503.7% |
| LSv3_Full | remiotore_ccxt-freqtrade | +1149.1% | 13.76 | 0% | 50901 | +878.9% | 13.21 | CHEATS (look-ahead bias) | +421.9% / +457.0% |
| NoTankAiV15D20241230 | RoboticAutomations_freqtradestrategies | +849.0% | 13.66 | 11% | 6673 | +545.6% | 9.57 | CHEATS (look-ahead bias) | +287.2% / +258.4% |
| NOTankAi_Futures | remiotore_ccxt-freqtrade | +955.7% | 11.85 | 2% | 8191 | +700.2% | 15.37 | CHEATS (look-ahead bias) | +371.5% / +328.8% |
| Pivot7 | remiotore_ccxt-freqtrade | +517.7% | 10.58 | 0% | 17067 | +413.8% | 9.67 | CHEATS (look-ahead bias) | +205.6% / +208.1% |
| el_rsiqui | remiotore_ccxt-freqtrade | +457.3% | 9.42 | 0% | 13125 | +324.3% | 7.30 | CHEATS (look-ahead bias) | +166.0% / +158.3% |
| Fengzi_v1 | remiotore_ccxt-freqtrade | +359.3% | 9.06 | 0% | 13774 | +357.2% | 9.46 | CHEATS (look-ahead bias) | +177.3% / +179.9% |
| ichiV1_plus | vaskosmihaylov_nfi-custom-strategies | +400.3% | 8.97 | 0% | 3235 | +239.1% | 6.24 | CHEATS (look-ahead bias) | +239.1% / +0.0% |
| InnovativeReversalStrategy | RoboticAutomations_freqtradestrategies | +73.3% | 7.25 | 0% | 81 | -11.8% | -0.28 | clean | -13.2% / +1.4% |
| mk2 | RoboticAutomations_freqtradestrategies | +254.1% | 7.08 | 0% | 15503 | +168.9% | 5.23 | CHEATS (look-ahead bias) | +74.2% / +94.7% |
| MQALYY | remiotore_ccxt-freqtrade | +73.2% | 5.22 | 0% | 56 | +8.3% | 2.59 | CHEATS (look-ahead bias) | +8.1% / +0.3% |
| RsiquiV3_2 | remiotore_ccxt-freqtrade | +194.2% | 4.46 | 0% | 5661 | +109.6% | 2.65 | CHEATS (look-ahead bias) | +41.8% / +67.8% |
| RsiquiV2 | remiotore_ccxt-freqtrade | +183.8% | 4.08 | 0% | 16738 | +129.0% | 3.16 | CHEATS (look-ahead bias) | +7.9% / +121.0% |

**19 of 20** stayed profitable in confirmation; **20** beat buy & hold (-47.5%).

## Strategies that cleared the luck bar

| strategy | select return | beyond luck | confirm return | look-ahead |
|---|---|---|---|---|
| DivergenceStrategy | +1399.3% | 100% | +1490.7% | CHEATS (look-ahead bias) |
| mk1 | +1088.9% | 100% | +947.7% | CHEATS (look-ahead bias) |
| SlopeV8 | +6571.0% | 100% | +6393.5% | CHEATS (look-ahead bias) |
| MSlopeV8 | +6571.0% | 100% | +6275.0% | CHEATS (look-ahead bias) |
| IchiVwapAdx | +522.4% | 100% | +438.4% | CHEATS (look-ahead bias) |
| NOTankAi_15_ali | +1161.3% | 100% | +781.8% | CHEATS (look-ahead bias) |

## Strategies that would not load

| reason | strategies |
|---|---|
| LOAD FAILED: 'No module named 'optuna'' | 22 |
| LOAD FAILED: 'name 'datetime' is not defined' | 3 |
| LOAD FAILED: 'name 'EI3v2_tag_cofi_green_Future_Long' is not defined' | 2 |
| LOAD FAILED: 'name 'Trade' is not defined' | 2 |
| LOAD FAILED: 'name 'MultiMA_TSL_461' is not defined' | 1 |
| LOAD FAILED: 'name 'BoombasticStrategy' is not defined' | 1 |
| LOAD FAILED: 'cannot import name 'NumericParameter' from 'freqtrade.strategy' (/opt/hosted | 1 |
| LOAD FAILED: 'name 'ichiV1' is not defined' | 1 |
| LOAD FAILED: 'name 'self' is not defined' | 1 |

## Backtest failures

| reason | strategies |
|---|---|
| timeout | 24 |
| numpy.exceptions.DTypePromotionError | 21 |
| TypeError | 14 |
| no result | 14 |
| memory | 8 |
|  | 5 |
| ValueError | 3 |
| AttributeError | 2 |
| KeyError | 2 |
| strategy BinHV27CombinedStrategy from 
'/home/runner/work/st | 1 |
| NameError | 1 |
| OSError | 1 |

Futures add liquidation risk and funding costs on top of everything above; leverage above 1x multiplies both gains and losses.

Research only, not financial advice. Third-party strategies were run unmodified; sources and commits are in sources_futures.txt.