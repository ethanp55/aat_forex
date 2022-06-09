from aat.assumptions import Assumptions, TechnicalIndicators
from market_proxy.currency_pairs import CurrencyPairs
from market_proxy.market_calculations import AMOUNT_TO_RISK
import numpy as np
from pandas import DataFrame
import pickle
from typing import Optional


class AatMarketTester:
    def __init__(self, risk_reward_ratio: float) -> None:
        self.risk_reward_ratio = risk_reward_ratio
        self.baseline = self.risk_reward_ratio * AMOUNT_TO_RISK

    def make_prediction(self, curr_idx: int, n_candles: int, market_data: DataFrame) -> float:
        pass


class KnnAatMarketTester(AatMarketTester):
    def __init__(self, risk_reward_ratio: float, currency_pair: Optional[CurrencyPairs] = None) -> None:
        AatMarketTester.__init__(self, risk_reward_ratio)
        self.currency_pair = currency_pair
        self.scaler = None
        self.knn_model = None
        self.training_data = None

    def make_prediction(self, curr_idx: int, n_candles: int, market_data: DataFrame) -> float:
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

        if self.scaler is None:
            scaler_path = f'../aat/training_data/{self.currency_pair.value}_trained_knn_scaler_aat.pickle' if \
                self.currency_pair is not None else '../aat/training_data/trained_knn_scaler_aat.pickle'
            knn_path = f'../aat/training_data/{self.currency_pair.value}_trained_knn_aat.pickle' if \
                self.currency_pair is not None else '../aat/training_data/trained_knn_aat.pickle'
            data_path = f'../aat/training_data/{self.currency_pair.value}_training_data.pickle' if \
                self.currency_pair is not None else '../aat/training_data/training_data.pickle'

            self.scaler = pickle.load(open(scaler_path, 'rb'))
            self.knn_model = pickle.load(open(knn_path, 'rb'))
            self.training_data = np.array(pickle.load(open(data_path, 'rb')))

        x = np.array(new_tup[0:-2]).reshape(1, -1)
        x_scaled = self.scaler.transform(x)
        neighbor_distances, neighbor_indices = self.knn_model.kneighbors(x_scaled, 15)

        corrections, distances = [], []

        for i in range(len(neighbor_indices[0])):
            neighbor_idx = neighbor_indices[0][i]
            neighbor_dist = neighbor_distances[0][i]
            corrections.append(self.training_data[neighbor_idx, -2])
            distances.append(neighbor_dist)

        trade_amount_pred, inverse_distance_sum = 0, 0

        for dist in distances:
            inverse_distance_sum += (1 / dist) if dist != 0 else (1 / 0.000001)

        for i in range(len(corrections)):
            distance_i, cor = distances[i], corrections[i]
            inverse_distance_i = (1 / distance_i) if distance_i != 0 else (1 / 0.000001)
            distance_weight = inverse_distance_i / inverse_distance_sum

            trade_amount_pred += (self.baseline * cor * distance_weight)

        return trade_amount_pred
