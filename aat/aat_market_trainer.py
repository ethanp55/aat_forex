from aat.assumptions import Assumptions, TechnicalIndicators
from market_proxy.market_calculations import AMOUNT_TO_RISK
from market_proxy.currency_pairs import CurrencyPairs
import numpy as np
from pandas import DataFrame
import pickle
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from typing import Optional


class AatMarketTrainer:
    def __init__(self, risk_reward_ratio: float) -> None:
        self.risk_reward_ratio = risk_reward_ratio
        self.baseline = self.risk_reward_ratio * AMOUNT_TO_RISK

    def record_tuple(self, curr_idx: int, n_candles: int, market_data: DataFrame) -> None:
        pass

    def trade_finished(self, net_profit: float) -> None:
        pass

    def save_data(self, currency_pair: Optional[CurrencyPairs] = None) -> None:
        pass


class KnnAatMarketTrainer(AatMarketTrainer):
    def __init__(self, risk_reward_ratio: float) -> None:
        AatMarketTrainer.__init__(self, risk_reward_ratio)
        self.training_data = []
        self.curr_trade_data = []

    def record_tuple(self, curr_idx: int, n_candles: int, market_data: DataFrame) -> None:
        ema200, ema100, atr, atr_sma, rsi, rsi_sma, adx, macd, macdsignal, slowk_rsi, slowd_rsi, vo, willy, \
            willy_ema = market_data.loc[market_data.index[curr_idx], ['ema200', 'ema100', 'atr', 'atr_sma', 'rsi',
                                                                      'rsi_sma', 'adx', 'macd', 'macdsignal',
                                                                      'slowk_rsi', 'slowd_rsi', 'vo', 'willy',
                                                                      'willy_ema']]

        ti_vals = TechnicalIndicators(ema200, ema100, atr, atr_sma, rsi, rsi_sma, adx, macd, macdsignal, slowk_rsi,
                                      slowd_rsi, vo, willy, willy_ema)
        prediction = self.baseline
        new_assumptions = Assumptions(n_candles, ti_vals, prediction)
        new_tup = new_assumptions.create_aat_tuple()

        self.curr_trade_data.append(new_tup)

    def trade_finished(self, net_profit: float) -> None:
        for tup in self.curr_trade_data:
            tup[-1] = net_profit
            tup[-2] = net_profit / tup[-2]

        self.training_data.extend(self.curr_trade_data)
        self.curr_trade_data.clear()

    def save_data(self, currency_pair: Optional[CurrencyPairs] = None) -> None:
        data_dir = '../aat/training_data'

        file_path = f'{data_dir}/{currency_pair.value}_training_data.pickle' if currency_pair is not None else \
            f'{data_dir}/training_data.pickle'

        with open(file_path, 'wb') as f:
            pickle.dump(self.training_data, f)

        x = np.array(self.training_data)[:, 0:-2]
        y = np.array(self.training_data)[:, -2]

        print('X train shape: ' + str(x.shape))
        print('Y train shape: ' + str(y.shape))

        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x)

        model = NearestNeighbors(n_neighbors=15)
        model.fit(x_scaled)

        trained_knn_file = f'{currency_pair.value}_trained_knn_aat.pickle' if currency_pair is not None else \
            'trained_knn_aat.pickle'
        trained_knn_scaler_file = f'{currency_pair.value}_trained_knn_scaler_aat.pickle' if currency_pair is not None \
            else 'trained_knn_scaler_aat.pickle'

        with open(f'{data_dir}/{trained_knn_file}', 'wb') as f:
            pickle.dump(model, f)

        with open(f'{data_dir}/{trained_knn_scaler_file}', 'wb') as f:
            pickle.dump(scaler, f)






