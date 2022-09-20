from aat.aat_market_tester import KnnAatMarketTester
from market_proxy.currency_pairs import CurrencyPairs
from strategy.directional_bars_strategy import DirectionalBarsStrategy

RISK_REWARD_RATIO = 1.5

bar_strategy = DirectionalBarsStrategy(5, RISK_REWARD_RATIO, 0.1, False, 3, 20, True)
currency_pair = CurrencyPairs.EUR_USD
date_range = '2020-2022'
aat_tester = KnnAatMarketTester(RISK_REWARD_RATIO, currency_pair)

# Test without AAT
print('RESULTS WITHOUT AAT')
results = bar_strategy.run_strategy(currency_pair, date_range)
print(f'Results for {currency_pair.value}:\n{results}')

# Test with AAT
print('RESULTS WITH AAT')
results = bar_strategy.run_strategy(currency_pair, date_range, aat_tester=aat_tester)
print(f'Results for {currency_pair.value}:\n{results}')


