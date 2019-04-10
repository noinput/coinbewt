import argparse
import configparser
import requests
import socket
import ssl
import time
import threading


class CoinBewt():

	def __init__(self, server, port, use_ssl, cmd_prefix, nickname, user, realname, channels):
		self.server = server
		self.port = port
		self.use_ssl = True if use_ssl == 'True' else False
		self.nickname = nickname
		self.user = user
		self.realname = realname
		self.channels = channels

		self.symbolDict = {}
		self.coinnameDict = {}
		self.cmd_prefix = f':{cmd_prefix}'

		t = threading.Thread(target=self._create_coin_db, daemon=True).start()

	def connect(self):
		self.socket = socket.socket()
		try:
			self.socket.connect((self.server, self.port))
			if self.use_ssl:
				self.socket = ssl.wrap_socket(self.socket)
		except (OSError, TimeoutError, socket.herror, socket.gaierror) as e:
			print(f'[!] {self.server}:{self.port} (ssl:{str(self.use_ssl)}) - FAILED:{e}')
		else:
			print(f'[+] Connected to {self.server}:{self.port}')
			self._send(f'NICK {self.nickname}')
			self._send(f'USER {self.user} 0 * :{self.realname}')

	def main(self):
		buff = b''
		while True:
			buff += self.socket.recv(1024)
			
			if not buff:
				print('socket is dead - reconnecting in 120 seconds..')
				time.sleep(120)
				self.connect()

			while b'\r\n' in buff:
				line, buff = buff.split(b'\r\n', 1)

				try:
					line = line.decode('utf-8')
				except UnicodeDecodeError:
					line = line.decode('iso-8859-1')

				print(f'<== {line}')

				split = line.split(' ')

				if split[0] == 'PING':
					self._send(f"PONG {split[1].split(':')[1]}")

				if split[1] == '376' or split[1] == '422':
					for c in self.channels:
						self._send(f'JOIN {c}')

				if split[1] == 'PRIVMSG':
					if split[2] != self.nickname:
						channel = split[2]
						if len(split) >= 5 and split[3] == self.cmd_prefix:
							t = threading.Thread(target=self._handle_cmd_prefix, args=(channel, split[3:]), daemon=True).start()


	def _handle_cmd_prefix(self, target, data):
			price = self._get_price(' '.join(data[1:]))
			if price:
				self._send(f'PRIVMSG {target} :{price}')

	def _send(self, data):
		print(f'==> {data}')
		self.socket.send(data.encode('utf-8') + b'\r\n')

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

	def _get_price(self, coin, fiat='USD'):
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

			return f'[\002{symbol}\002] {name} is {price_fiat} ({change24h} /24H) | {price_btc} | {price_eth}'


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', help='configfile (default: config.ini)', default='config.ini')

	configfile = parser.parse_args().config

	cf = configparser.ConfigParser()
	cf.read(configfile)
	coinconfig = {}

	for i, v in cf.items('coinBewt'):
		coinconfig[i] = v

	bot = CoinBewt(
		server=coinconfig['server'], 
		port=int(coinconfig['port']),
		use_ssl=coinconfig['use_ssl'],
		cmd_prefix=coinconfig['cmd_prefix'],
		nickname=coinconfig['nickname'],
		user=coinconfig['user'],
		realname=coinconfig['realname'],
		channels=coinconfig['channels'].split())

	bot.connect()
	bot.main()