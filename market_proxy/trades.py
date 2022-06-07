from dataclasses import dataclass
import enum
from pandas._libs.tslib import Timestamp


class TradeType(enum.Enum):
    BUY = 1
    SELL = 2


@dataclass
class Trade:
    trade_type: TradeType
    open_price: float
    stop_loss: float
    stop_gain: float
    n_units: int
    original_units: int
    start_date: Timestamp
    end_date: Timestamp
