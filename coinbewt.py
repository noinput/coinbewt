import argparse
import configparser
from resources.ircbewt import IrcBewt
from resources.bewthelper import CoinDB, CoinTop, BtcHalv, Corona

# callback function
def handle_callback(target, data):
    if data[1] == 'halving':
        bot.send(f'PRIVMSG {target} :{_BtcHalv.get_halv()}')
    
    elif data[1] == 'top':
        bot.send(f'PRIVMSG {target} :{_CoinTop.get_top()}')        
    
    elif data[1] == 'corona':
        irc_country = ' '.join(data[2:])
        corona_stats = _Corona.get_corona_stats_for_country(irc_country)
        
        if corona_stats is not False:
            bot.send(f'PRIVMSG {target} :{corona_stats}')        
        else:
            bot.send(f'PRIVMSG {target} :\002[{irc_country}]\002 country not found')   
    else:
        price = _CoinDb.get_price(' '.join(data[1:]))
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
    
    _CoinDb = CoinDB(fiat=coinconfig['fiat'])
    _CoinTop = CoinTop(fiat=coinconfig['fiat'])
    _BtcHalv = BtcHalv()
    _Corona = Corona()

    try:
        bot.connect()
        bot.main()
    except KeyboardInterrupt:
        bot.disconnect()
        bot.die()

