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
realname=voted hottest and most likely to succeed 2020
quitmsg=ded.
channels=#coinBewt #crypto
cmd_prefix=?
callback=handle_callback
fiat=USD
```

### start the bot
```
python coinbewt.py [-c configfile - default: config.ini]
```

# Commands
```
13:07:58 @noinput: ? bitcoin
13:07:59 coinBewt: [BTC] Bitcoin is $3,845.30 (+0.82% today) | Ƀ 1.00 | Ξ 27.63
13:08:07 @noinput: ? ethereum
13:08:08 coinBewt: [ETH] Ethereum is $139.95 (+2.41% today) | Ƀ 0.03619 | Ξ 1.00
13:08:14 @noinput: ? foobar
13:08:14 coinBewt: [foobar] no such coin
```
```
15:21:40 @noinput: ? halving
15:21:40 coinBewt: Bitcoin Halving is 16438 blocks, 114 days, 3 hours and 40 minutes away! (12.05.2020 18:01 UTC)
```
```
15:21:41 @noinput: ? top
15:21:41 coinBewt: BTC $8,633.17 (-3.12%) | XRP $0.2323 (-3.73%) | ETH $164.59 (-7.02%) | BCH $331.23 (-7.94%) | BSV $249.88 (-3.66%) | USDT $0.9985 (-0.05%) | EOS $3.56 (-8.94%) | LTC $56.48 (-7.5%) | BRC $5.41 (+0.11%)
```
