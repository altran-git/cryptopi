#!/usr/bin/python

import json
import time
import Adafruit_CharLCD as LCD
from urllib.request import urlopen

lcd = LCD.Adafruit_CharLCDPlate()

def get_spaces(symbol, percent):
    spaces = 16-len(symbol)-len('%+.2f'%(percent))-1
    return spaces

while True:
    symbol_list = ['BTC', 'ETH', 'SC', 'STORJ', 'MAID']
    url = "https://min-api.cryptocompare.com/data/histohour?fsym=ETH&tsym=USD&limit=24"
    data_24hr = json.loads(urlopen(url).read().decode('utf-8'))

    # for data in data_24hr['Data']:
    #     print(data)

    old = data_24hr['Data'][0]['close']
    new = data_24hr['Data'][-1]['close']

    diff_perc_24hr = round((new/old-1)*100, 2)

    if diff_perc_24hr >= 0:
        #Green
        lcd.set_color(0, 1, 0)
    else:
        #Red
        lcd.set_color(1, 0, 0)

    lcd.clear()
    spaces = get_spaces('ETH', diff_perc_24hr)
    message = 'ETH{}{}%\n${}'.format(' '*spaces, '%+.2f'%(diff_perc_24hr), new)
    lcd.message(message)
    time.sleep(15)







