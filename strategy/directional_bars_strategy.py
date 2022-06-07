from pandas import DataFrame
from market_proxy.currency_pairs import CurrencyPairs
from market_proxy.market_calculations import MarketCalculations
from market_proxy.trades import Trade, TradeType
from typing import Optional
from strategy.strategy import Strategy


class DirectionalBarsStrategy(Strategy):
    def __init__(self, description: str, starting_idx: int, risk_reward_ratio: float, spread_cutoff: float,
                 each_bar: bool, n_bars: int, pip_movement: int, use_pullback: bool):
        Strategy.__init__(self, description, starting_idx)
        self.risk_reward_ratio = risk_reward_ratio
        self.spread_cutoff = spread_cutoff
        self.each_bar = each_bar
        self.n_bars = n_bars
        self.pip_movement = pip_movement
        self.use_pullback = use_pullback
        self.lookback = self.n_bars + 1 if self.use_pullback else n_bars
        self.starting_idx = self.lookback
        self.lookforward = -1 if self.use_pullback else 0

    def place_trade(self, curr_idx: int, market_data: DataFrame, currency_pair: CurrencyPairs) -> Optional[Trade]:
        curr_bid_open, curr_bid_high, curr_bid_low, curr_ask_open, curr_ask_high, curr_ask_low, curr_mid_open, \
            curr_date = market_data.loc[market_data.index[curr_idx], ['Bid_Open', 'Bid_High', 'Bid_Low', 'Ask_Open',
                                                                      'Ask_High', 'Ask_Low', 'Mid_Open', 'Date']]
        spread = abs(curr_ask_open - curr_bid_open)

        mid_opens = list(
            market_data.loc[market_data.index[curr_idx - self.lookback:curr_idx + self.lookforward], 'Mid_Open'])
        mid_highs = list(
            market_data.loc[market_data.index[curr_idx - self.lookback:curr_idx + self.lookforward], 'Mid_High'])
        mid_lows = list(
            market_data.loc[market_data.index[curr_idx - self.lookback:curr_idx + self.lookforward], 'Mid_Low'])
        mid_closes = list(
            market_data.loc[market_data.index[curr_idx - self.lookback:curr_idx + self.lookforward], 'Mid_Close'])

        if self.each_bar:
            buy_signal = all(
                [mid_opens[j] < mid_closes[j] and abs(mid_opens[j] - mid_closes[j]) >= self.pip_movement for j in
                 range(len(mid_opens))])
            sell_signal = all(
                [mid_opens[j] > mid_closes[j] and abs(mid_opens[j] - mid_closes[j]) >= self.pip_movement for j in
                 range(len(mid_opens))])

        else:
            buy_signal = all([mid_opens[j] < mid_closes[j] for j in range(len(mid_opens))]) and abs(
                mid_opens[0] - mid_closes[-1]) >= self.pip_movement
            sell_signal = all([mid_opens[j] > mid_closes[j] for j in range(len(mid_opens))]) and abs(
                mid_opens[0] - mid_closes[-1]) >= self.pip_movement

        if self.use_pullback and buy_signal:
            mid_open1, mid_high1, mid_low1, mid_close1 = market_data.loc[
                market_data.index[curr_idx - 1], ['Mid_Open', 'Mid_High', 'Mid_Low', 'Mid_Close']]
            buy_signal = mid_open1 > mid_close1 and abs(mid_close1 - mid_open1) <= 0.25 * abs(mid_high1 - mid_low1)

        if self.use_pullback and sell_signal:
            mid_open1, mid_high1, mid_low1, mid_close1 = market_data.loc[
                market_data.index[curr_idx - 1], ['Mid_Open', 'Mid_High', 'Mid_Low', 'Mid_Close']]
            sell_signal = mid_open1 < mid_close1 and abs(mid_close1 - mid_open1) <= 0.25 * abs(mid_high1 - mid_low1)

        highest_high, lowest_low = max(mid_highs), min(mid_lows)

        trade = None

        if buy_signal:
            open_price = curr_ask_open
            stop_loss = lowest_low

            if stop_loss < open_price:
                curr_pips_to_risk = open_price - stop_loss

                if spread <= curr_pips_to_risk * self.spread_cutoff:
                    stop_gain = open_price + (self.risk_reward_ratio * curr_pips_to_risk)
                    trade_type = TradeType.BUY
                    n_units = MarketCalculations.get_n_units(trade_type, stop_loss, curr_ask_open, curr_bid_open,
                                                             curr_mid_open, currency_pair)

                    trade = Trade(trade_type, open_price, stop_loss, stop_gain, n_units, n_units, curr_pips_to_risk,
                                  curr_date, None)

        elif sell_signal:
            open_price = float(curr_bid_open)
            stop_loss = highest_high

            if stop_loss > open_price:
                curr_pips_to_risk = stop_loss - open_price

                if spread <= curr_pips_to_risk * self.spread_cutoff:
                    stop_gain = open_price - (self.risk_reward_ratio * curr_pips_to_risk)
                    trade_type = TradeType.SELL
                    n_units = MarketCalculations.get_n_units(trade_type, stop_loss, curr_ask_open, curr_bid_open,
                                                             curr_mid_open, currency_pair)

                    trade = Trade(trade_type, open_price, stop_loss, stop_gain, n_units, n_units, curr_pips_to_risk,
                                  curr_date, None)

        return trade