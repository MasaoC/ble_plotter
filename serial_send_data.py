#開発テスト用ファイル
#PC/MAC から、OLEDにシリアルを送信するためのファイル。

import math
import serial
import time

writeSer = serial.Serial('/dev/tty.usbserial-A901OEG6',38400, timeout=3)

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