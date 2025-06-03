# 開発テスト用ファイル
# このファイルは、PC/MAC から、BLE/OLEDデバイス (ESP32C3) にシリアル送信し、BLEを発信させる。
# このファイルを実行する際は、このMac/PC　又は 近隣のMac/PC　でble.py が実行されている状態が想定される。
# つまり、このスクリプト-(USB-Serial)-> BLE/OLED[ESP32C3] -(無線BLE)-> 近隣のPC/MAC or このPC/MAC
# requires pyserial


import math
import serial
import serial.tools.list_ports
import time

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

def main():
	port = choose_serial_port()
	if port:
		try:
			writeSer = serial.Serial(port, 38400, timeout=3)
			print(f"Connected to {port} at 38400 baud.")
			for x in range(50000):
				airspeed = abs(math.sin(x/30)*5.0+2.0)
				ruddertrim = 1.0+ 0 if x%720<360 else math.sin(x*4*3.1415/180)
				elevatortrim = -1.0+ 0 if x%720>360 else math.sin(x*4*3.1415/180)
				rudder = math.cos(x/5)*6
				elevator = math.sin(45+x/3)*2
				#airspeed,rudder,rudder_trim,elevator,elevator_trim\n")
				texttosave = "{:.2f}".format(airspeed)+","+"{:.2f}".format(rudder+ruddertrim)+","+"{:.2f}".format(ruddertrim)+","+"{:.2f}".format(elevator+elevatortrim)+","+"{:.2f}".format(elevatortrim)+"\n"

				writeSer.write(texttosave.encode())
				writeSer.write(("#"+texttosave).encode())
				time.sleep(0.1);
				print(" ",x," sending        ", end="\r")

			writeSer.close()
		except Exception as e:
			print(f"Failed to connect: {e}")

if __name__ == "__main__":
	main()
