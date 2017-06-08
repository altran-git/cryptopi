#!/usr/bin/python

import json
import time
import threading
import Adafruit_CharLCD as LCD
from urllib.request import urlopen

lcd = LCD.Adafruit_CharLCDPlate()
lcd.create_char(1, [4, 30, 21, 30, 21, 30, 4, 0]) #Create BTC symbol

def get_spaces(symbol, percent):
    spaces = 16-len(symbol)-len('%+.2f'%(percent))-1
    return spaces

class Worker(threading.Thread):
    def __init__(self, fsym, tsym):
        threading.Thread.__init__(self)
        self.fsym = fsym
        self.tsym = tsym
        self.data_24hr = None
        self.restart = False
        self.toggle = False

    def run(self):
        while True:
            url = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym={}&limit=24'.format(self.fsym.upper(),self.tsym.upper())
            self.data_24hr = json.loads(urlopen(url).read().decode('utf-8'))
            lcd.clear()
            start_time = time.time()
            elapsed_time = 0
            self.restart = False
            while self.restart is not True and elapsed_time < 10:
                old = self.data_24hr['Data'][0]['close']
                new = self.data_24hr['Data'][-1]['close']

                diff_perc_24hr = round((new / old - 1) * 100, 2)

                if diff_perc_24hr >= 0:
                    lcd.set_color(0, 1, 0)  # Green
                else:
                    lcd.set_color(1, 0, 0)  # Red

                lcd.home()
                if self.toggle != True:
                    spaces = get_spaces(self.fsym, diff_perc_24hr)
                    if self.tsym == 'USD':
                        message = '{}{}{}%\n${}'.format(self.fsym, ' ' * spaces, '%+.2f' % (diff_perc_24hr), new)
                    elif self.tsym == 'BTC':
                        message = '{}{}{}%\n{}{}'.format(self.fsym, ' ' * spaces, '%+.2f' % (diff_perc_24hr), '\x01', new)
                    else:
                        message = '{}{}{}%\n{}'.format(self.fsym, ' ' * spaces, '%+.2f' % (diff_perc_24hr), new)
                else:
                    message = '\n {}'.format(new)
                lcd.message(message)
                
                time.sleep(.1)
                elapsed_time = time.time() - start_time

    def set_sym(self, fsym, tsym):
        self.fsym = fsym
        self.tsym = tsym

    def toggle_details(self):
        self.toggle = not self.toggle

    def restart_worker(self):
        self.restart = True

if __name__ == '__main__':
    fsym_list = ['BTC', 'ETH', 'SC', 'SJCX', 'MAID']
    tsym_list = ['USD', 'BTC']
    fsym_idx = 0
    tsym_idx = 0
    fsym_max = len(fsym_list)
    tsym_max = len(tsym_list)

    worker = Worker(fsym_list[0], 'USD')
    worker.start()

    while True:
        if lcd.is_pressed(LCD.SELECT):
            worker.restart_worker()
        elif lcd.is_pressed(LCD.LEFT):
            fsym_idx -= 1
            if fsym_idx == -1:
                fsym_idx = fsym_max - 1
            if fsym_list[fsym_idx] == tsym_list[tsym_idx]:
                tsym_idx += 1
                if tsym_idx == tsym_max:
                    tsym_idx = 0
            worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx])
            worker.restart_worker()
        elif lcd.is_pressed(LCD.RIGHT):
            fsym_idx += 1
            if fsym_idx == fsym_max:
                fsym_idx = 0
            if fsym_list[fsym_idx] == tsym_list[tsym_idx]:
                tsym_idx += 1
                if tsym_idx == tsym_max:
                    tsym_idx = 0
            worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx])
            worker.restart_worker()
        elif lcd.is_pressed(LCD.UP):
            worker.toggle_details()
            worker.restart_worker()
        elif lcd.is_pressed(LCD.DOWN):
            tsym_idx += 1
            if tsym_idx == fsym_max:
                tsym_idx = 0
            if fsym_list[fsym_idx] == tsym_list[tsym_idx]:
                tsym_idx += 1
                if tsym_idx == tsym_max:
                    tsym_idx = 0
            worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx])
            worker.restart_worker()

        time.sleep(.1)
