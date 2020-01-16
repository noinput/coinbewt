import json
import requests
import threading
import time

from datetime import datetime, timedelta


class BtcHalv():
    
    def __init__(self):
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8'}

    def get_halv(self):
        r = requests.get(f'https://blockchain.info/stats?format=json', headers=self.headers)

        if r.status_code == 200:

            data = r.json()

            current_block = int(data['n_blocks_total'])
            
            # A bitcoin halving occurs each 210 000 block
            blocks_left = 210000 - current_block % 210000
            
            # seconds left till next halving - assume 10 minute blocks (avg)
            seconds_left = blocks_left * 10 * 60
            
            days = seconds_left // 86400
            hours = seconds_left // 3600 % 24
            minutes = seconds_left // 60 % 60
            seconds = seconds_left % 60

            dt = datetime.utcnow()
            td = timedelta(seconds=seconds_left)

            halving_date = dt + td

            return f"\002Bitcoin Halving\002 is \002{blocks_left}\002 blocks, {days} days, {hours} hours and {minutes} minutes away! (\002{halving_date.strftime('%d.%m.%Y %H:%M')} UTC\002)"


class CoinDB():
    
    def __init__(self):
        self.symbolDict = {}
        self.coinnameDict = {}
        
        t = threading.Thread(target=self._create_coin_db, daemon=True).start()
    
    def _create_coin_db(self, sleeptime=84600):
        api_resource = 'https://min-api.cryptocompare.com/data/all/coinlist'

        while True:
            r = requests.get(api_resource, timeout=20)

            if r.status_code == 200:
                data = r.json()
                i = 0

                for entry in data['Data'].items():
                    if 'Symbol' in entry[1] and 'CoinName' in entry[1]:
                        symbol = entry[1]['Symbol']
                        coinname = entry[1]['CoinName']

                        # build a cache that is searchable by both short and full name
                        self.coinnameDict[coinname.upper()] = {'symbol': symbol, 'name': coinname}
                        self.symbolDict[symbol.upper()] = {'symbol': symbol, 'name': coinname}

                        i += 1

                print(f'[+] {i} coins cached - sleeping for {sleeptime} seconds..')
                time.sleep(sleeptime)

    def _find_coin(self, coin):
        coin = coin.upper()
        if self.coinnameDict.get(coin):
            return self.coinnameDict.get(coin)
        elif self.symbolDict.get(coin):
            return self.symbolDict.get(coin)
        else:
            return {'symbol': coin, 'name': coin}

    def get_price(self, coin, fiat='USD'):
        td = self._find_coin(coin)
        symbol = td['symbol']
        name = td['name']

        api_resource = f'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbol}&tsyms={fiat},BTC,ETH'

        r = requests.get(api_resource, timeout=5)

        if r.status_code == 200:
            data = r.json()

            if 'Response' in data and data['Response'] == 'Error':
                return f'[\002{coin}\002] no such coin'

            price_fiat = data['DISPLAY'][symbol][fiat]['PRICE'].replace(' ', '')
            price_btc = data['DISPLAY'][symbol]['BTC']['PRICE']
            price_eth = data['DISPLAY'][symbol]['ETH']['PRICE']

            change24h = float(round(data['RAW'][symbol][fiat]['CHANGEPCT24HOUR'], 2))
            change24h = f'\00303+{change24h}%\003' if change24h > 0 else f'\00304{change24h}%\003'

            return f'[\002{symbol}\002] {name} is {price_fiat} ({change24h}) | {price_btc} | {price_eth}'