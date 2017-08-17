#!/usr/bin/python

import json
import time
import threading
import Adafruit_CharLCD as LCD
from urllib.request import urlopen

lcd_columns = 16
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
        self.break_error = False

    def run(self):
        while True:
            url = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym={}&limit=24'.format(self.fsym.upper(),self.tsym.upper())
            try:
                self.data_24hr = json.loads(urlopen(url).read().decode('utf-8'))
            except Exception as e:
                print("URL Load error.")
                time.sleep(.1)
                continue
            lcd.clear()
            try:
                if self.data_24hr['Response'].upper().strip() == 'ERROR':
                    self.break_error = False
                    message = self.data_24hr['Message'].upper()
                    for i in range((len(message) - 16)+(len(message) % 16)):
                        if self.break_error:
                            break
                        lcd.clear()
                        lcd.message('ERROR:\n{}'.format(message[i:(i + 16)]))
                        time.sleep(0.03)
                elif self.data_24hr['Response'].upper().strip() == 'SUCCESS':
                    start_time = time.time()
                    elapsed_time = 0
                    self.restart = False
                    while self.restart is not True and elapsed_time < 10:
                        old = self.data_24hr['Data'][0]['close']
                        new = self.data_24hr['Data'][-1]['close']
                        
                        if old == 0:
                            diff_perc_24hr = 0
                        else:
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
                else:
                    print("Error: Unknown Response")
            except Exception as e:
                print("Data processing error.")
                time.sleep(.1)
                continue

    def set_sym(self, fsym, tsym):
        self.fsym = fsym
        self.tsym = tsym

    def toggle_details(self):
        self.toggle = not self.toggle

    def set_break_error(self):
        self.break_error = True

    def restart_worker(self):
        self.restart = True

def debounce(button):
    counter = 0
    while True:
        reading = lcd.is_pressed(button)
        if reading == True:
            counter = 0
        else:
            counter += 1
        if counter == 30:
            return
        time.sleep(.01)

if __name__ == '__main__':
    with open('symbols.txt', 'r') as fsym_list:
        fsym_list = [i.upper().strip() for i in fsym_list if i.upper().strip() != '']
    tsym_list = ['USD', 'BTC']
    fsym_idx = 0
    tsym_idx = 0
    fsym_max = len(fsym_list)
    tsym_max = len(tsym_list)
    cycle = False

    worker = Worker(fsym_list[fsym_idx], tsym_list[tsym_idx])
    worker.start()

    while True:
        if lcd.is_pressed(LCD.SELECT):
            debounce(LCD.SELECT)
            cycle = not cycle
            # worker.restart_worker()
        elif lcd.is_pressed(LCD.LEFT):
            debounce(LCD.LEFT)
            fsym_idx -= 1
            if fsym_idx == -1:
                fsym_idx = fsym_max - 1
            if fsym_list[fsym_idx] == tsym_list[tsym_idx]:
                if tsym_idx + 1 == tsym_max:
                    worker.set_sym(fsym_list[fsym_idx], tsym_list[0])
                else:
                    worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx+1])
            else:
                worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx])
            worker.set_break_error()
            worker.restart_worker()
        elif lcd.is_pressed(LCD.RIGHT):
            debounce(LCD.RIGHT)
            fsym_idx += 1
            if fsym_idx == fsym_max:
                fsym_idx = 0
            if fsym_list[fsym_idx] == tsym_list[tsym_idx]:
                if tsym_idx + 1 == tsym_max:
                    worker.set_sym(fsym_list[fsym_idx], tsym_list[0])
                else:
                    worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx+1])
            else:
                worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx])
            worker.set_break_error()
            worker.restart_worker()
        elif lcd.is_pressed(LCD.UP):
            debounce(LCD.UP)
            worker.toggle_details()
            worker.restart_worker()
        elif lcd.is_pressed(LCD.DOWN):
            debounce(LCD.DOWN)
            tsym_idx += 1
            if tsym_idx == tsym_max:
                tsym_idx = 0
            if fsym_list[fsym_idx] == tsym_list[tsym_idx]:
                if tsym_idx + 1 == tsym_max:
                    worker.set_sym(fsym_list[fsym_idx], tsym_list[0])
                else:
                    worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx+1])
            else:
                worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx])
            worker.restart_worker()

        if cycle is True:
            fsym_idx += 1
            if fsym_idx == fsym_max:
                fsym_idx = 0
            if fsym_list[fsym_idx] == tsym_list[tsym_idx]:
                if tsym_idx + 1 == tsym_max:
                    worker.set_sym(fsym_list[fsym_idx], tsym_list[0])
                else:
                    worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx+1])
            else:
                worker.set_sym(fsym_list[fsym_idx], tsym_list[tsym_idx])
            worker.set_break_error()
            worker.restart_worker()
            time.sleep(3)

        time.sleep(.1)
