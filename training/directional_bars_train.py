from aat.aat_market_trainer import KnnAatMarketTrainer
from market_proxy.currency_pairs import CurrencyPairs
from strategy.directional_bars_strategy import DirectionalBarsStrategy

RISK_REWARD_RATIO = 2.0

bar_strategy = DirectionalBarsStrategy(0, RISK_REWARD_RATIO, 0.1, False, 3, 20, True)
knn_trainer = KnnAatMarketTrainer(CurrencyPairs.EUR_USD, RISK_REWARD_RATIO)

results = bar_strategy.run_strategy(knn_trainer.currency_pair, knn_trainer)

print(results)
