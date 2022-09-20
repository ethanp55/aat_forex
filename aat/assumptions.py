from dataclasses import dataclass
from typing import List


@dataclass
class TechnicalIndicators:
    ema200: float
    ema100: float
    atr: float
    atr_sma: float
    rsi: float
    rsi_sma: float
    adx: float
    macd: float
    macdsignal: float
    slowk_rsi: float
    slowd_rsi: float
    vo: float
    willy: float
    willy_ema: float

    def get_values(self) -> List[float]:
        attribute_names = self.__annotations__.keys()
        return [self.__getattribute__(field_name) for field_name in attribute_names]

    def bool_values(self) -> List[int]:
        up_trend = self.ema100 > self.ema100
        down_trend = self.ema100 < self.ema200
        atr_up_trend = self.atr > self.atr_sma
        atr_down_trend = self.atr < self.atr_sma
        rsi_up_trend = self.rsi > self.rsi_sma
        rsi_down_trend = self.rsi < self.rsi_sma
        rsi_buy = self.rsi > 50
        rsi_sell = self.rsi < 50
        adx_small = self.adx > 20
        adx_medium = self.adx > 25
        adx_large = self.adx > 30
        macd_up = min([self.macd, self.macdsignal, 0]) == 0
        macd_down = max([self.macd, self.macdsignal, 0]) == 0
        volume_small = self.vo > 0
        volume_medium = self.vo > 0.10
        volume_large = self.vo > 0.20
        willy_up_trend = self.willy > self.willy_ema
        willy_down_trend = self.willy < self.willy_ema

        return [up_trend, down_trend, atr_up_trend, atr_down_trend, rsi_up_trend, rsi_down_trend, rsi_buy, rsi_sell,
                adx_small, adx_medium, adx_large, macd_up, macd_down, volume_small, volume_medium, volume_large,
                willy_up_trend, willy_down_trend]


class Assumptions:
    def __init__(self, n_candles_since_open: int, ti_vals: TechnicalIndicators, prediction: float) -> None:
        self.n_candles_since_open = float(n_candles_since_open)
        self.ti_vals = ti_vals
        self.prediction = prediction

    def create_aat_tuple(self) -> List[float]:
        return [self.n_candles_since_open] + self.ti_vals.get_values() + [self.prediction, self.prediction]

    def create_aat_bool_tuple(self) -> List[float]:
        return [self.n_candles_since_open] + self.ti_vals.bool_values() + [self.prediction, self.prediction]
