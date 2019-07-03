# coinBewt
A simple bot for IRC written in Python that will look up the price of cryptocurrencies
using the public API from cryptocompare.com

* Requires Python 3.6 or higher

## Getting started
Modify the config file to fit your needs, defaults:
```
[coinBewt]
server=chat.freenode.net
port=7000
use_ssl=True
nickname=coinBewt
altnickname=coinBewt__
user=coinBewt
realname=voted hottest and most likely to succeed 2019
channels=#coinBewt #crypto
cmd_prefix=?
```

### start the bot
```
python coinbewt.py [-c configfile - default: config.ini]
```

# Example output
```
13:07:58 @noinput: ? bitcoin
13:07:59 coinBewt: [BTC] Bitcoin is $3,845.30 (+0.82% today) | Ƀ 1.00 | Ξ 27.63
13:08:07 @noinput: ? ethereum
13:08:08 coinBewt: [ETH] Ethereum is $139.95 (+2.41% today) | Ƀ 0.03619 | Ξ 1.00
13:08:14 @noinput: ? foobar
13:08:14 coinBewt: [foobar] no such coin
```
