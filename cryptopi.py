#!/usr/bin/python

import json
import time
import Adafruit_CharLCD as LCD
from urllib.request import urlopen

url = "https://min-api.cryptocompare.com/data/histohour?fsym=ETH&tsym=USD&limit=24&e=Coinbase"
data_24hr = json.loads(urlopen(url).read().decode('utf-8'))

for data in data_24hr['Data']:
    print(data)

old = data_24hr['Data'][0]['close']
new = data_24hr['Data'][-1]['close']

diff_perc_24hr = round((new/old-1)*100, 2)
print(diff_perc_24hr)

lcd = LCD.Adafruit_CharLCDPlate()

if diff_perc_24hr > 0:
    #Green
    lcd.set_color(0, 1, 0)
    lcd.clear()
    lcd.message('ETH\n+{}%'.format(diff_perc_24hr))
elif diff_perc_24hr < 0:
    #Red
    lcd.set_color(1, 0, 0)
    lcd.clear()
    lcd.message('ETH\n-{}%'.format(diff_perc_24hr))
else:
    #White
    lcd.set_color(1, 1, 1)
    lcd.clear()
    lcd.message('ETH\n+{}%'.format(diff_perc_24hr))





