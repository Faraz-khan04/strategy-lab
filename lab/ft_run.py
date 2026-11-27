"""Run a freqtrade command. In futures mode every strategy's leverage() is replaced by the lab's fixed
leverage, whatever the author wrote (some hard-code 10x or more).
Usage: python -m lab.ft_run <freqtrade args...>"""
import sys

from freqtrade.main import main
from freqtrade.resolvers import strategy_resolver

from .settings import LEVERAGE, MODE

if MODE == "futures" and not getattr(strategy_resolver.StrategyResolver.load_strategy, "_lab_forced", False):
    _orig = strategy_resolver.StrategyResolver.load_strategy

    def _load(config=None):
        strategy = _orig(config)
        strategy.leverage = lambda *a, **k: LEVERAGE     # instance attribute wins over the class method
        return strategy

    _load._lab_forced = True
    strategy_resolver.StrategyResolver.load_strategy = staticmethod(_load)

if __name__ == "__main__":
    main(sys.argv[1:])
