"""Write the single Freqtrade config every strategy is tested with."""
import json
import sys

from .settings import EXCHANGE_FOR_MARKETS, MAX_OPEN, MODE, PAIRS, QUOTE, STAKE, WALLET


def config(datadir):
    return {
        "max_open_trades": MAX_OPEN, "stake_currency": QUOTE, "stake_amount": STAKE, "dry_run_wallet": WALLET,
        "tradable_balance_ratio": 1.0, "dry_run": True,
        "trading_mode": MODE, "margin_mode": "isolated" if MODE == "futures" else "",
        "timeframe": "5m",                                   # each strategy's own timeframe takes precedence
        "exchange": {"name": EXCHANGE_FOR_MARKETS, "key": "", "secret": "",
                     "pair_whitelist": [f"{p}/{QUOTE}" + (f":{QUOTE}" if MODE == "futures" else "") for p in PAIRS],
                     "pair_blacklist": []},
        "pairlists": [{"method": "StaticPairList"}],
        "entry_pricing": {"price_side": "other", "use_order_book": False, "price_last_balance": 0.0},
        "exit_pricing": {"price_side": "other", "use_order_book": False},
        "datadir": datadir, "dataformat_ohlcv": "feather",
        "internals": {"process_throttle_secs": 5},
    }


if __name__ == "__main__":
    json.dump(config(sys.argv[2]), open(sys.argv[1], "w"), indent=1)
