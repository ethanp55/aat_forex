from market_proxy.currency_pairs import CurrencyPairs
import pandas as pd


class DataRetriever(object):
    @staticmethod
    def get_data_for_pair(currency_pair: CurrencyPairs) -> pd.DataFrame:
        df = pd.read_csv(f'../market_proxy/data/Oanda_{currency_pair.value}_M5_2021-2022.csv')

        return df
