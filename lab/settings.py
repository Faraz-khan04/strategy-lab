"""Every fixed choice of the test, decided before any result was seen."""
PAIRS = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX", "LINK", "LTC"]   # all traded the whole period
QUOTE = "USDT"
TIMEFRAMES = ["5m", "15m", "30m", "1h", "2h", "4h", "1d"]
DATA_FROM, DATA_TO = "2022-07", "2026-10"          # months; the first months feed indicator warm-up only
PERIODS = {
    "select":  "20230101-20250101",                # where the best strategies are picked
    "confirm": "20250101-20261101",                # where the picks have to hold up
}
FEE = 0.001                                         # 0.1% per side, Binance spot taker
WALLET, STAKE, MAX_OPEN = 10_000, 1_000, 5
MIN_TRADES = 30                                     # fewer trades than this in a period: too few to judge
TOP_PICKS = 20                                      # how many selection-period leaders we follow into confirmation
DSR_PASS = 0.95                                     # deflated Sharpe probability needed to count as "beyond luck"
BACKTEST_TIMEOUT = 20 * 60                          # seconds per strategy per period
EXCHANGE_FOR_MARKETS = "okx"                        # only supplies pair metadata; prices come from Binance archives
