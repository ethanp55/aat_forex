from pandas import DataFrame
from strategy.strategy import Strategy
from strategy.strategy_results import StrategyResults


class MarketSimulator(object):
    @staticmethod
    def run_simulation(strategy: Strategy, market_data: DataFrame) -> StrategyResults:
        pass

        

