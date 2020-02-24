import os
import json
import time
import requests
from os import path
import urllib.request
from operator import itemgetter

from bittrex import bittrex
from playsound import playsound


class PumpCheck:
    bittrex_api = bittrex('#####', '#####') # bittrex api key and secret

    def __init__(self):

        self.change_check = 100
        self.bittrex_change_check = 30
        self.binance_change_check = 30
        self.exchanges = ['binance', 'bittrex']
        self.final_results = []
        self.coinex_results = []
        self.hitbtc_results = []
        self.bittrex_results = []
        self.binance_results = []

        with open('markets.json', 'r') as f:
            self.coinex_markets = json.load(f)
        try:
            for exchange in self.exchanges:
                self.get_results(exchange)
        except Exception as e:
            print(e)
        else:
            self.print_results()


    # Find common coins
    def get_results(self, exchange):

        if exchange == 'hitbtc':
            self.hitbtc_data()
        elif exchange == 'coinex':
            self.coinex_data()
        elif exchange == 'bittrex':
            self.bittrex_data()
        elif exchange == 'binance':
            self.binance_data()

    ##
    # Check Prices Individuals
    ##
    def hitbtc_data(self):
        url = 'https://api.hitbtc.com/api/2/public/ticker'
        json_data = requests.get(url).json()
        for item in json_data:
            current = float(item['last'])
            price_24 = float(item['low'])
            change = ((current - price_24) / price_24) * 100
            if change > self.change_check:
                result = {"Coin": item['symbol'], "Exchange": 'Hitbtc', "Change": change}
                self.hitbtc_results.append(result)

    def coinex_data(self):
        # By using the Api
        url = 'https://www.coinexchange.io/api/v1/getmarketsummaries'
        json_data = requests.get(url).json()['result']
        for item in json_data:
            change = float(item['Change'])
            if change > self.change_check:
                market_id = item['MarketID']
                coinSymbol = [i for i in self.coinex_markets if i['MarketID'] == market_id][0]['MarketAssetCode']
                baseSymbol = [i for i in self.coinex_markets if i['MarketID'] == market_id][0]['BaseCurrencyCode']
                result = {"Coin": coinSymbol+baseSymbol, "Exchange": 'Coinex', "Change": change}
                self.coinex_results.append(result)

    def bittrex_data(self):
        summary = self.bittrex_api.getmarketsummaries()
        for item in summary:
            market = item['MarketName']
            if market.startswith('BTC-'):
                coin = market[4:]
                try:
                    low = item['Low']
                    last = item['Last']
                    change = ((last - low) / low) * 100
                    if change > self.bittrex_change_check:
                        result = {"Coin": coin, "Exchange": 'Bittrex', "Change": change}
                        self.bittrex_results.append(result)
                except Exception as e:
                    print(coin, e)

    def binance_data(self):
        url = "https://api.binance.com/api/v1/ticker/24hr"
        summary = requests.get(url).json()
        for item in summary:
            symbol = item["symbol"]
            if symbol.endswith("BTC"):
                coin = symbol[:-3]
                change = float(item["priceChangePercent"])
                if change > self.binance_change_check:
                    result = {"Coin": coin, "Exchange": 'Binance', "Change": change}
                    self.binance_results.append(result)


    def print_results(self):
        self.coinex_results = sorted(self.coinex_results, key=itemgetter('Change'), reverse=True)
        self.hitbtc_results = sorted(self.hitbtc_results, key=itemgetter('Change'), reverse=True)
        self.bittrex_results = sorted(self.bittrex_results, key=itemgetter('Change'), reverse=True)
        self.binance_results = sorted(self.binance_results, key=itemgetter('Change'), reverse=True)

        # Clear Screen
        os.system('cls')

        if self.coinex_results:
            print("Coinex Results:")
            for item in self.coinex_results:
                print(item["Coin"], item["Change"])
            print("\n")
        if self.hitbtc_results:
            print("Hitbtc Results:")
            for item in self.hitbtc_results:
                print(item["Coin"], item["Change"])
            print("\n")
        if self.bittrex_results:
            print("Bittrex Results:")
            for item in self.bittrex_results:
                print(item["Coin"], item["Change"])
            print("\n")
        if self.binance_results:
            print("Binance Results:")
            for item in self.binance_results:
                print(item["Coin"], item["Change"])
            print("\n")

        # Check for new results and save results
        with open('results.txt', 'r') as results_file:
            saved_results = json.load(results_file)
            new_results = self.coinex_results + self.hitbtc_results + self.bittrex_results + self.binance_results

            # Check for new results
            saved_coins = []
            for item in saved_results:
                saved_coin = item["Coin"]+item["Exchange"]
                saved_coins.append(saved_coin)
            new_coins = []
            for item in new_results:
                new_coin = item["Coin"]+item["Exchange"]
                new_coins.append(new_coin)
            saved_results_set = set(saved_coins)
            new_results_set = set(new_coins)
            diff = new_results_set - saved_results_set

            # Play sound if new resutls
            if len(diff):
                playsound('pumping.mp3')

        with open('results.txt', 'w') as results_file:
            json.dump(new_results, results_file)


if __name__ == '__main__':

    while True:
        try:
            while True:
                i = PumpCheck()
                print('Restarting in 60 seconds...')
                time.sleep(60)
        except Exception as e:
            print(e)
            print('Some error occured retrying in 60 seconds')
        time.sleep(60)

