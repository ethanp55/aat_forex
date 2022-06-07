from dataclasses import dataclass


@dataclass
class StrategyResults:
    reward: float
    day_fees: float
    net_reward: float
    avg_pips_risked: float
    n_buys: int
    n_sells: int
    n_wins: int
    n_losses: int
    longest_win_streak: int
    longest_loss_streak: int
