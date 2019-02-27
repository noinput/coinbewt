import requests
import socket
import ssl
import time
import threading


class CoinBewt():

	def __init__(self, server, port, use_ssl, cmd_prefix, nickname, username, realname, channels):
		self.server = server
		self.port = port
		self.use_ssl = use_ssl
		self.nickname = nickname
		self.username = username
		self.realname = realname
		self.channels = channels
		self.connected = False

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
			self._send(f'USER {self.username} 0 * :{self.realname}')
			self.connected = True

	def main(self):
		buff = b''
		while self.connected:
			buff += self.socket.recv(1024)

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
						if len(split) >= 4 and split[3] == self.cmd_prefix:
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

			return f'[\002{symbol}\002] {name} is {price_fiat} ({change24h} today) | {price_btc} | {price_eth}'


if __name__ == '__main__':
	server = 'chat.freenode.net'
	port = 7000
	use_ssl = True
	nickname = 'coinBewt'
	user = 'coinBewt'
	realname = 'voted hottest and most likely to succeed 2019'
	channels = ['#coinBewt', '#crypto']

	cmd_prefix = '?'

	bot = CoinBewt(server, port, use_ssl, cmd_prefix, nickname, user, realname, channels)
	bot.connect()
	bot.main()