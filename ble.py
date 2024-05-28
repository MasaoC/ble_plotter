
'''
    File name: ble.py
    Author: Masao Chiguchi
    Date created: 2024/05/26
    Date last modified: 2024/5/28
    Python Version: 3.10.0 (tested on)

    メインの BLE 受信、グラフ起動ファイル。
    BLEとの通信を確立し、受信したデータをCSVファイルを新たに作成し保存する。
    ファイル名は自動生成し、最新のファイル名が「setting_plotter.txt」に保存される。
'''

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import time
import numpy as np
import matplotlib.pyplot as plt
import threading
import subprocess
import datetime


timestr = time.strftime("csv%Y%m%d-%H%M")
csvf = open("./csv/"+timestr+".csv", "w")
csvf.write("time,airspeed,rudder,rudder_trim,elevator,elevator_trim\n")
csvf.flush()


rawsavedata = open("./csv/raw.csv", "a")

NAME_OLED = "ALBA TAIYO OLED v2"


ble = BLERadio()

uart_connection = None


print("This ble.py will connect to ble-oled "+NAME_OLED+"and saves csv file to [./csv/" + timestr + ".csv]. and settings file(setting_plotter.txt) have been changed.")

settingf = open("setting_plotter.txt", "w")
settingf.write(timestr+".csv")
settingf.close()

#マルチスレッド。プロッター表示。
def run_script(script_name):
    subprocess.run(["python", script_name])

script1_thread = threading.Thread(target=run_script, args=("plotter.py",))
script1_thread.start()


while True:
    if not uart_connection:
        print("Trying to connect...")
        for adv in ble.start_scan(ProvideServicesAdvertisement):
            print(adv.complete_name)
            if UARTService in adv.services and adv.complete_name == NAME_OLED:
                uart_connection = ble.connect(adv)
                print("Connected!" + NAME_OLED)
                break
        ble.stop_scan()



    if uart_connection and uart_connection.connected:
        uart_service = uart_connection[UARTService]
        print(uart_service)
        while uart_connection.connected:
            getinput = uart_service.readline()
            if getinput == None or len(getinput) == 0:
                print("no signal....")
                time.sleep(1)
                continue

            print("DATA="+getinput.decode("utf-8"), end="")#¥nすでに含まれているため。end=""
            inputvalues = getinput.decode("utf-8").split(",")

            rawsavedata.write(getinput.decode("utf-8"))
            rawsavedata.flush()
            #正しくsplitできた時のみCSV保存実行
            if len(inputvalues) == 5:
                now = datetime.datetime.now()
                csvf.write(now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]+","+getinput.decode("utf-8"))
                csvf.flush()


csvf.close()




