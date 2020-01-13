import argparse
import configparser
from .resources.ircbewt import IrcBewt
from .resources.bewthelper import CoinDB, BtcHalv


# callback function
def handle_callback(target, data):
	if bot.is_connected:
		if data[1] == 'halving':
			bot.send(f'PRIVMSG {target} :{halv.get_halv()}')
		else:
			price = coinDb.get_price(' '.join(data[1:]))
			if price:
				bot.send(f'PRIVMSG {target} :{price}')

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', help='configfile (default: config.ini)', default='config.ini')

	configfile = parser.parse_args().config

	cf = configparser.ConfigParser()
	cf.read(configfile)
	coinconfig = {}
	
	for k, v in cf.items('coinBewt'):
		coinconfig[k] = v

	bot = IrcBewt(
		server=coinconfig['server'], 
		port=int(coinconfig['port']),
		use_ssl=coinconfig['use_ssl'],
		cmd_prefix=coinconfig['cmd_prefix'],
		nickname=coinconfig['nickname'],
		altnickname=coinconfig['altnickname'],
		user=coinconfig['user'],
		realname=coinconfig['realname'],
		channels=coinconfig['channels'].split(),
		quitmsg=coinconfig['quitmsg'],
		callback=handle_callback)
	
	coinDb = CoinDB()
	halv = BtcHalv()

	try:
		bot.connect()
		bot.main()
	except KeyboardInterrupt:
		bot.die()

