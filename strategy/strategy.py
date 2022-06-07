from pandas import DataFrame


class Strategy:
    def __init__(self, description: str, starting_idx: int) -> None:
        self.description = description
        self.starting_idx = starting_idx

    def should_place_trade(self, curr_idx: int, market_data: DataFrame):
        pass
