
'''
    File name: ble.py
    Author: Masao Chiguchi
    Date created: 2024/05/26
    Date last modified: 2024/5/28
    Python Version: 3.10.0 (tested on)

    メインの BLE 受信ファイル。グラフ起動(plotter.py実行)も行う。
    BLEとの通信を確立し、受信したデータをCSVファイルを新たに作成し保存する。
    ファイル名は自動生成し、最新のファイル名が「setting_plotter.txt」に保存される。
'''
import time, sys, threading, subprocess, datetime

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from colorama import Fore, Back, Style


RAWDATAPATH = "./csv/raw.csv"
RAWDATAPATH_RELAY = "./csv/raw_relay.csv"
NAME_OLED = "ALBA TAIYO OLED v2"
NAME_RELAY = "BLE RELAY"

Path("./csv/").mkdir(parents=True, exist_ok=True)
#Creating new save file.
timestr = time.strftime("csv%Y%m%d-%H%M")
csvf = open("./csv/"+timestr+".csv", "w")
csvf.write("time,airspeed,rudder,rudder_trim,elevator,elevator_trim\n")
csvf.flush()
#Creating new relay save file.
csvf_relay = open("./csv/"+timestr+"_relay.csv", "w")
csvf_relay.write("time,airspeed,rudder,rudder_trim,elevator,elevator_trim\n")
csvf_relay.flush()

#Creating appending rawdata save file.
rawsavedataf = open(RAWDATAPATH, "a")
rawsavedataf_relay = open(RAWDATAPATH_RELAY, "a")


print("[INIT. PROCESS] This ble.py will connect to ble-oled "+NAME_OLED+".")
print("Saves csv file to [./csv/" + timestr + ".csv]. and [./csv/"+timestr+"_relay.csv]")

settingf = open("setting_plotter.txt", "w")
settingf.write(timestr+".csv\n")
settingf.write(timestr+"_relay.csv\n")
settingf.close()
print("settings file(setting_plotter.txt) has been changed.")


ble = BLERadio()
uart_connection,uart_relay_connection = None,None

#マルチスレッド。プロッター表示。
def run_script(script_name):
    subprocess.run(["python", script_name])

script1_thread = None
uart_thread, uartrelay_thread = None, None


while True:
    if not uart_connection or not uart_relay_connection:
        print("Trying to connect...")
        connect_begin_time = datetime.datetime.now()
        for adv in ble.start_scan(ProvideServicesAdvertisement):
            if UARTService in adv.services:
                if adv.complete_name == NAME_OLED and not uart_connection:
                    uart_connection = ble.connect(adv)
                    print("Connected!" + NAME_OLED+"[RSSI="+str(adv.rssi)+"]")
                elif adv.complete_name == NAME_RELAY and not uart_relay_connection:
                    uart_relay_connection = ble.connect(adv)
                    print("Relay Connected!" + NAME_RELAY+"[RSSI="+str(adv.rssi)+"]")
                else:
                    if not adv.complete_name in [NAME_RELAY,NAME_OLED]:
                        print("FOUND NORDIC UART SERVICE, but the name does not match."+NAME_RELAY+","+NAME_OLED+"<>["+adv.complete_name+"]")                    
            else:
                if adv.complete_name:
                    print("NOT UART:" + adv.complete_name)
                else:
                    print("NOT UART:.")
            #リレーおよび本体が見つかった
            if uart_connection and uart_relay_connection:
                print(f"{Fore.GREEN}{Back.BLACK}BLE AND RELAY, BOTH CONNECTED!{Style.RESET_ALL}")
                break

            time_elapsed = (datetime.datetime.now() - connect_begin_time).total_seconds() 

            if time_elapsed > 10 and not uart_relay_connection and uart_connection:
                print(f"{Fore.RED}No relay found!! continue...{Style.RESET_ALL}")
                break
            elif time_elapsed > 15 and not uart_connection and uart_relay_connection:
                print(f"{Fore.RED}Only the relay connected!! continue...{Style.RESET_ALL}")
                break
            elif time_elapsed > 20:
                print(f"{Fore.RED}No device found, but continue scan...{Style.RESET_ALL}")
                connect_begin_time = datetime.datetime.now()
            
        ble.stop_scan()

    #Creating plotter window.
    if not script1_thread:
        script1_thread = threading.Thread(target=run_script, args=("plotter.py",))
        script1_thread.start()


    #どちらかがつながっている間実行
    def print_write_this_to(inputdata, rawfile, csvfile):
        if not inputdata:
            return
        decoded = inputdata.decode("utf-8")
        #print("DATA="+decoded, end="")#¥nすでに含まれているため。end=""
        rawfile.write(decoded)
        rawfile.flush()

        inputvalues = decoded.split(",")
        if len(inputvalues) == 5:
            now = datetime.datetime.now()
            csvfile.write(now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]+","+decoded)
            csvfile.flush()
        else:
            print(f"{Fore.RED}FORMAT ERR:{decoded}{Style.RESET_ALL}")

    def check_connection_and_readline(waiting_uart, rawfile, csvfile, name):
        while waiting_uart and waiting_uart.connected:
            getinput = waiting_uart[UARTService].readline()
            print_write_this_to(getinput, rawfile, csvfile)

        print(f"{Fore.RED}{name} disconnected{Style.RESET_ALL}")


    if uart_connection and not uart_thread:
        uart_thread = threading.Thread(target=check_connection_and_readline, args=(uart_connection, rawsavedataf, csvf, NAME_OLED))
        uart_thread.start()

    if uart_relay_connection and not uartrelay_thread:
        uartrelay_thread = threading.Thread(target=check_connection_and_readline, args=(uart_relay_connection, rawsavedataf_relay, csvf_relay, NAME_RELAY))
        uartrelay_thread.start()


    if uart_thread and uartrelay_thread:
        #Both direct and relay connected.
        while True:
            if not uart_thread.is_alive():
                uart_thread = None
                uart_connection = None
                print(f"{Fore.RED}Trying to reestablish direct connection.{Style.RESET_ALL}")
                break
            if not uartrelay_thread.is_alive():
                uartrelay_thread = None
                uart_relay_connection = None
                print(f"{Fore.RED}Trying to reestablish relay connection.{Style.RESET_ALL}")
                break
            time.sleep(1)

    elif uartrelay_thread and not uart_thread:
        #If no direct connection
        print(f"{Fore.RED}Trying to establish direct connection.{Style.RESET_ALL}")
        continue
    elif uart_thread and not uartrelay_thread:
        #If no relay connection
        print(f"{Fore.RED}Trying to establish relay connection.{Style.RESET_ALL}")
        continue

csvf.close()
rawsavedata.close()




