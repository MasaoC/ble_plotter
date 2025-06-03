'''
    File name: usbcom_logger.py
    Author: Masao Chiguchi
    Date created: 2024/06/3
    Date last modified: 2026/6/3
    Python Version: 3.10.0 (tested on)

    Mac/PC上の最新のCSVにUSBCOMのデータを直接書き込む。BLEを介さない。
    「setting_plotter.txt」を更新する。
 '''


import time
import threading
import datetime
import serial
import serial.tools.list_ports
import math
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init()

SETTING_FILE = "setting_plotter.txt"
RAWDATAPATH = "./csv/raw.csv"
NUM_VALID_DATA = 5  # Assuming 5 values: time, airspeed, elevator, elevator_trim, rudder, rudder_trim

# CSVヘッダー
orderdata = "time,airspeed,elevator,elevator_trim,rudder,rudder_trim\n"

def initialize_csv():
	Path("./csv/").mkdir(parents=True, exist_ok=True)
	# Creating new save file
	timestr = time.strftime("usb%Y%m%d-%H%M")
	csv_path = f"./csv/{timestr}.csv"
	
	with open(csv_path, "w") as csvf:
		csvf.write(orderdata)
		csvf.flush()

	with open(SETTING_FILE, "w") as settingf:
		settingf.write(timestr + ".csv\n")
	
	print(f"Settings file ({SETTING_FILE}) has been changed for direct USB connection.")
	return csv_path

def list_serial_ports():
	ports = serial.tools.list_ports.comports()
	return [port.device for port in ports]

def choose_serial_port():
	ports = list_serial_ports()
	if not ports:
		print("No serial ports found.")
		return None

	print("Available serial ports:")
	for i, port in enumerate(ports):
		print(f"{i + 1}: {port}")

	while True:
		choice = input("Select the port number to connect: ")
		if choice.isdigit():
			choice_num = int(choice)
			if 1 <= choice_num <= len(ports):
				return ports[choice_num - 1]
		print("Invalid choice. Please enter a valid number.")

def debug_sendserialdata(serial_port):
	while True:
		time.sleep(0.1)
		x = time.time()  # 時間ベースでxを生成
		airspeed = abs(math.sin(x/30) * 5.0 + 2.0)
		ruddertrim = 1.0 if x % 720 < 360 else math.sin(x * 4 * math.pi / 180)
		elevatortrim = -1.0 if x % 720 > 360 else math.sin(x * 4 * math.pi / 180)
		rudder = math.cos(x/5) * 6
		elevator = math.sin(45 + x/3) * 2
		texttosave = f"{airspeed:.2f},{rudder+ruddertrim:.2f},{ruddertrim:.2f},{elevator+elevatortrim:.2f},{elevatortrim:.2f}\n"
		
		serial_port.write(texttosave.encode())
		print("sending", end="\r")

def main():
	csv_path = initialize_csv()
	port = choose_serial_port()
	
	if not port:
		return
	
	try:
		with serial.Serial(port, 9600, timeout=3) as readSer:
			print(f"Connected to {port} at 9600 baud.")

			# デバッグ用スレッド
			#debug_sendcomdata_thread = threading.Thread(target=debug_sendserialdata, args=(readSer,))
			#debug_sendcomdata_thread.start()
			
			with open(RAWDATAPATH, "a") as rawsavedataf, open(csv_path, "a") as csvfile:
				while True:
					try:
						inputdata = readSer.readline()
						if not inputdata:
							continue
						print(inputdata)
						decoded = inputdata.decode("utf-8").strip()
						# print(f"DATA={decoded}")
						
						rawsavedataf.write(decoded + "\n")
						rawsavedataf.flush()

						inputvalues = decoded.split(",")
						if len(inputvalues) == NUM_VALID_DATA:
							now = datetime.datetime.now()
							csvfile.write(now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + "," + decoded + "\n")
							csvfile.flush()
						else:
							print(f"{Fore.RED}FORMAT ERR:{decoded}{Style.RESET_ALL}")
							
					except UnicodeDecodeError:
						print(f"{Fore.RED}Decode error occurred{Style.RESET_ALL}")
					except serial.SerialException:
						print(f"{Fore.RED}Serial port disconnected{Style.RESET_ALL}")
						break
					except KeyboardInterrupt:
						print(f"{Fore.RED}Program terminated by user{Style.RESET_ALL}")
						break

	except Exception as e:
		print(f"{Fore.RED}Failed to connect: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
	main()