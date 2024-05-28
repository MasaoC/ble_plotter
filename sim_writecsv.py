#開発テスト用ファイル
#直接、最新のCSVに仮想のデータを書き込む

import time
import math
import datetime

settingf = open("setting_plotter.txt", "r")
csvfilename = settingf.readline()
print(csvfilename)



csvf = open("./csv/"+csvfilename, "a")

for x in range(5000):
	now = datetime.datetime.now()
	timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	airspeed = abs(math.sin(x/30)*5.0+2.0)
	ruddertrim = 1.0+ 0 if x%720<360 else math.sin(x*4*3.1415/180)
	elevatortrim = -1.0+ 0 if x%720>360 else math.sin(x*4*3.1415/180)
	rudder = math.cos(x/5)*6
	elevator = math.sin(45+x/3)*2
	#time,airspeed,rudder,rudder_trim,elevator,elevator_trim\n")
	texttosave = timestamp+",{:.2f}".format(airspeed)+","+"{:.2f}".format(rudder+ruddertrim)+","+"{:.2f}".format(ruddertrim)+","+"{:.2f}".format(elevator+elevatortrim)+","+"{:.2f}".format(elevatortrim)+"\n"

	csvf.write(texttosave)
	csvf.flush()
	time.sleep(0.1);
csvf.close()