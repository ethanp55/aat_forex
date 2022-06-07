from pandas import DataFrame
from market_proxy.currency_pairs import CurrencyPairs
from market_proxy.trades import Trade
from typing import Optional

class Strategy:
    def __init__(self, description: str, starting_idx: int) -> None:
        self.description = description
        self.starting_idx = starting_idx

    def place_trade(self, curr_idx: int, market_data: DataFrame, currency_pair: CurrencyPairs) -> Optional[Trade]:
        pass
