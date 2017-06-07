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

    def run(self):
        while True:
            url = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym={}&limit=24'.format(self.fsym.upper(),self.tsym.upper())
            self.data_24hr = json.loads(urlopen(url).read().decode('utf-8'))

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

                lcd.clear()
                spaces = get_spaces(self.fsym, diff_perc_24hr)
                message = '{}{}{}%\n${}'.format(self.fsym, ' ' * spaces, '%+.2f' % (diff_perc_24hr), new)
                lcd.message(message)
                
                time.sleep(.1)
                elapsed_time = time.time() - start_time


    def set_sym(self, fsym, tsym):
        self.fsym = fsym
        self.tsym = tsym

    def restart_worker(self):
        self.restart = True

def debounce(button):
    debounce_delay = 500
    current_button_state = True
    last_button_state = True
    last_debounce_time = 0
    while True:
        print("HERE")
        reading = lcd.is_pressed(button)

        if reading != last_button_state:
            print("HERE0")
            last_debounce_time = time.time()
        if ((time.time() - last_debounce_time)/1000) > debounce_delay:
            print("HERE1")
            if reading != current_button_state:
                print("HERE2")
                current_button_state = reading
            if current_button_state == True:
                print("DEBOUNCED")
                return True

        last_button_state = reading

if __name__ == '__main__':
    symbol_list = ['BTC', 'ETH', 'SC', 'SJCX', 'MAID']
    idx = 0
    max = len(symbol_list)

    worker = Worker(symbol_list[0], 'USD')
    worker.start()

    while True:
        # temp = int(input())
        # if temp == 1:
        #     worker.set_sym('BTC', 'USD')
        # elif temp == 2:
        #     worker.restart_worker()

        if lcd.is_pressed(LCD.SELECT):
            debounce(LCD.SELECT)
            worker.restart_worker()
        elif lcd.is_pressed(LCD.LEFT):
            debounce(LCD.LEFT)
            idx -= 1
            if idx == -1:
                idx = max - 1
            worker.set_sym(symbol_list[idx], 'USD')
            worker.restart_worker()
        elif lcd.is_pressed(LCD.RIGHT):
            debounce(LCD.RIGHT)
            idx += 1
            if idx == max:
                idx = 0
            worker.set_sym(symbol_list[idx], 'USD')
            worker.restart_worker()
        elif lcd.is_pressed(LCD.UP):
            debounce(LCD.UP)
            pass
        elif lcd.is_pressed(LCD.DOWN):
            debounce(LCD.DOWN)
            pass

        time.sleep(.1)

    # for data in data_24hr['Data']:
    #     print(data)








