from aat.aat_market_trainer import KnnAatMarketTrainer
from market_proxy.currency_pairs import CurrencyPairs
from strategy.directional_bars_strategy import DirectionalBarsStrategy

RISK_REWARD_RATIO = 1.5

bar_strategy = DirectionalBarsStrategy(5, RISK_REWARD_RATIO, 0.1, False, 3, 20, True)
knn_trainer = KnnAatMarketTrainer(RISK_REWARD_RATIO)
currency_pair = CurrencyPairs.EUR_USD
date_range = '2016-2020'

results = bar_strategy.run_strategy(currency_pair, date_range, knn_trainer)
print(f'Results for {currency_pair.value}:\n{results}')

knn_trainer.save_data(currency_pair)
