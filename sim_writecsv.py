# 開発テスト用ファイル
# Mac/PCから、Mac/PC上の最新のCSVに仮想のデータを直接書き込む。BLEを介さない。

import time
import math
import datetime

settingf = open("setting_plotter.txt", "r")
csvfilename = settingf.readline().rstrip('\n')
csvfilename_relay = settingf.readline().rstrip('\n')
print(csvfilename, csvfilename_relay)

csvf = open("./csv/"+csvfilename, "a")
csvf_relay = open("./csv/"+csvfilename_relay, "a")

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

	if (x/50)%3 < 1:
		csvf.write(texttosave)
		csvf.flush()
	elif (x/50)%3 < 2:
		csvf_relay.write(texttosave)
		csvf_relay.flush()

	time.sleep(0.1);
csvf.close()
csvf_relay.close()