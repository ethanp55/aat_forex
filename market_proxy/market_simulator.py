from aat.aat_market_trainer import AatMarketTrainer
from datetime import datetime
from pandas import DataFrame
from market_proxy.market_calculations import MarketCalculations
from market_proxy.trades import TradeType
import numpy as np
from strategy.strategy_class import Strategy
from strategy.strategy_results import StrategyResults
from typing import Optional


class MarketSimulator(object):
    @staticmethod
    def run_simulation(strategy: Strategy, market_data: DataFrame, aat_trainer: Optional[AatMarketTrainer] = None) -> \
            StrategyResults:
        reward, n_wins, n_losses, win_streak, loss_streak, curr_win_streak, curr_loss_streak, n_buys, n_sells, \
            day_fees = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  # Numerical results we keep track of
        pips_risked, trade, n_candles = [], None, 0

        for idx in range(strategy.starting_idx, len(market_data)):
            n_candles += 1

            # If there is no open trade, check to see if we should place one
            if trade is None:
                trade = strategy.place_trade(idx, market_data)

                if trade is not None:
                    pips_risked.append(trade.pips_risked)
                    n_candles = 0

                    if trade.trade_type == TradeType.BUY:
                        n_buys += 1

                    elif trade.trade_type == TradeType.SELL:
                        n_sells += 1

                    else:
                        raise Exception(f'Invalid trade type on the following trade: {trade}')

            # If there is an open trade, check to see if it should close out (there are 4 conditions)
            # For each condition, we set the trade's end date; update the reward, num wins, num losses, etc.; close
            # the trade (set it to None); and continue to the next iteration in the simulation loop (continue to the
            # next candle)
            if trade is not None:
                if aat_trainer is not None:
                    aat_trainer.record_tuple(idx, n_candles, market_data)

                curr_bid_open, curr_bid_high, curr_bid_low, curr_ask_open, curr_ask_high, curr_ask_low, curr_mid_open, \
                    curr_date = market_data.loc[market_data.index[idx], ['Bid_Open', 'Bid_High', 'Bid_Low', 'Ask_Open',
                                                                         'Ask_High', 'Ask_Low', 'Mid_Open', 'Date']]

                # Condition 1 - trade is a buy and the stop loss is hit
                if trade.trade_type == TradeType.BUY and curr_bid_low <= trade.stop_loss:
                    trade.end_date = datetime.strptime(curr_date, '%Y-%m-%d %H:%M:%S')
                    trade_amount = (trade.stop_loss - trade.open_price) * trade.n_units
                    reward += trade_amount
                    day_fees += MarketCalculations.calculate_day_fees(trade)

                    n_wins += 1 if trade_amount > 0 else 0
                    n_losses += 1 if trade_amount < 0 else 0
                    curr_win_streak = 0 if trade_amount < 0 else curr_win_streak + 1
                    curr_loss_streak = 0 if trade_amount > 0 else curr_loss_streak + 1

                    if curr_win_streak > win_streak:
                        win_streak = curr_win_streak

                    if curr_loss_streak > loss_streak:
                        loss_streak = curr_loss_streak

                    trade = None

                    if aat_trainer is not None:
                        aat_trainer.trade_finished(trade_amount + day_fees)

                    continue

                # Condition 2 - Trade is a buy and the take profit/stop gain is hit
                if trade.trade_type == TradeType.BUY and curr_bid_high >= trade.stop_gain:
                    trade.end_date = datetime.strptime(curr_date, '%Y-%m-%d %H:%M:%S')
                    trade_amount = (trade.stop_gain - trade.open_price) * trade.n_units
                    reward += trade_amount
                    day_fees += MarketCalculations.calculate_day_fees(trade)

                    n_wins += 1 if trade_amount > 0 else 0
                    n_losses += 1 if trade_amount < 0 else 0
                    curr_win_streak = 0 if trade_amount < 0 else curr_win_streak + 1
                    curr_loss_streak = 0 if trade_amount > 0 else curr_loss_streak + 1

                    if curr_win_streak > win_streak:
                        win_streak = curr_win_streak

                    if curr_loss_streak > loss_streak:
                        loss_streak = curr_loss_streak

                    trade = None

                    if aat_trainer is not None:
                        aat_trainer.trade_finished(trade_amount + day_fees)

                    continue

                # Condition 3 - trade is a sell and the stop loss is hit
                if trade.trade_type == TradeType.SELL and curr_ask_high >= trade.stop_loss:
                    trade.end_date = datetime.strptime(curr_date, '%Y-%m-%d %H:%M:%S')
                    trade_amount = (trade.open_price - trade.stop_loss) * trade.n_units
                    reward += trade_amount
                    day_fees += MarketCalculations.calculate_day_fees(trade)

                    n_wins += 1 if trade_amount > 0 else 0
                    n_losses += 1 if trade_amount < 0 else 0
                    curr_win_streak = 0 if trade_amount < 0 else curr_win_streak + 1
                    curr_loss_streak = 0 if trade_amount > 0 else curr_loss_streak + 1

                    if curr_win_streak > win_streak:
                        win_streak = curr_win_streak

                    if curr_loss_streak > loss_streak:
                        loss_streak = curr_loss_streak

                    trade = None

                    if aat_trainer is not None:
                        aat_trainer.trade_finished(trade_amount + day_fees)

                    continue

                # Condition 4 - Trade is a sell and the take profit/stop gain is hit
                if trade.trade_type == TradeType.SELL and curr_ask_low <= trade.stop_gain:
                    trade.end_date = datetime.strptime(curr_date, '%Y-%m-%d %H:%M:%S')
                    trade_amount = (trade.open_price - trade.stop_gain) * trade.n_units
                    reward += trade_amount
                    day_fees += MarketCalculations.calculate_day_fees(trade)

                    n_wins += 1 if trade_amount > 0 else 0
                    n_losses += 1 if trade_amount < 0 else 0
                    curr_win_streak = 0 if trade_amount < 0 else curr_win_streak + 1
                    curr_loss_streak = 0 if trade_amount > 0 else curr_loss_streak + 1

                    if curr_win_streak > win_streak:
                        win_streak = curr_win_streak

                    if curr_loss_streak > loss_streak:
                        loss_streak = curr_loss_streak

                    trade = None

                    if aat_trainer is not None:
                        aat_trainer.trade_finished(trade_amount + day_fees)

                    continue

        # Record any AAT training data
        if aat_trainer is not None:
            aat_trainer.save_data()

        # Return the simulation results once we've iterated through all the data
        avg_pips_risked = np.array(pips_risked).mean() if len(pips_risked) > 0 else np.nan

        results = StrategyResults(reward, day_fees, reward + day_fees, avg_pips_risked, n_buys, n_sells, n_wins,
                                  n_losses, win_streak, loss_streak)

        return results
