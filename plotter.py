

'''
    File name: plotter.py
    Author: Masao Chiguchi
    Date created: 2024/05/26
    Date last modified: 2024/5/28
    Python Version: 3.10.0 (tested on)

	CSVファイルを開き、グラフ化する
	最新のCSVファイル名は「setting_plotter.txt」から読み込む。
'''

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
import time
from datetime import datetime
import random


DRAW_INTERVAL = 100 #100=10Hz

settingf = open("setting_plotter.txt", "r")
csvfilename = settingf.readline().rstrip('\n')
csvfilename_relay = settingf.readline().rstrip('\n')

graph_title = csvfilename.replace(".csv", "").replace("csv","")

print(csvfilename)

# ツールバー非表示
matplotlib.rcParams['toolbar'] = 'None'

# グラフ表示領域を2つ生成し、6:1の表示領域（エルロンピッチ:風速）とする。
fig, (ax1,ax2) = plt.subplots(2, 1, figsize=(4,5), facecolor='lightblue',gridspec_kw={'height_ratios': [6, 1]})

# 最大対気速度を記録する変数
maxspdval = 0

# 風速表示
barcollection = ax2.barh([0,1],[0,maxspdval],height=[1,0.3], color=["blue","aqua"])

# 線や点の設定
ln, = ax1.plot([], [], color='blue', marker='o',linewidth=1 ,markersize=7, alpha=1)
ln2, = ax1.plot([], [], color='blue', marker='o',linewidth=1 ,markersize=2, alpha=0.5)
ln3, = ax1.plot([], [], color='red', marker='o',linewidth=1 ,markersize=5, alpha=0.5)


#color='blue', marker='o',markersize=10, linewidth=0)
def init():
	ax1.set_xlabel("LEFT   <-   ->   RIGHT")
	ax1.set_ylabel("UP   <-   ->   DOWN")
	ax1.plot([-20,20],[0,0],c='black')
	ax1.plot([0,0],[-20,20],c='black')
	ax1.grid()
	ax1.set_xlim(-16,16)
	ax1.set_ylim(-8,8)
	ax1.set_title(graph_title)
	ax1.invert_yaxis()

	ax2.grid(axis = 'x')
	ax2.set_xlim(0,10)
	ax2.invert_yaxis()
	#ax2.xaxis.set_visible(False)
	ax2.set_yticks([0,1], labels=["SPD","Max"])
	ax2.set_xticks(range(11))
	plt.tight_layout()

	return ln,


def barlist(n): 
    return [1/float(n*k) for k in range(1,6)]

def animate(frame):
	global maxspdval
	timebegin = datetime.now()
	data = pd.read_csv("./csv/"+csvfilename)
	data.apply(pd.to_numeric, errors='coerce')
	data_relay = pd.read_csv("./csv/"+csvfilename_relay)
	data_relay.apply(pd.to_numeric, errors='coerce')

	data_time,data_relay_time = None, None
	direct_online, relay_online = False, False
	use_relay = False

	#軌跡の表示のため、データが６個以上集まっていれば有効とみなす。3秒以内受信かつ５個データが2秒以内が必須(2.5Hz)
	if len(data['time']) > 6:
		data_time = datetime.strptime(data['time'].iloc[-1],'%Y-%m-%d %H:%M:%S.%f')
		data_time_5 = datetime.strptime(data['time'].iloc[-5],'%Y-%m-%d %H:%M:%S.%f')
		direct_online = (datetime.now()-data_time).total_seconds() < 3 and (data_time - data_time_5).total_seconds() < 2
	if len(data_relay['time']) > 6:
		data_relay_time = datetime.strptime(data_relay['time'].iloc[-1],'%Y-%m-%d %H:%M:%S.%f')
		data_relay_time_5 = datetime.strptime(data_relay['time'].iloc[-5],'%Y-%m-%d %H:%M:%S.%f')
		relay_online = (datetime.now()-data_relay_time).total_seconds() < 3 and (data_relay_time - data_relay_time_5).total_seconds() < 2

	if not direct_online and not relay_online:
		ax2.set_title("OFFLINE", loc='right', fontsize=9, color='red')
	elif not direct_online and relay_online:
		use_relay = True
		ax2.set_title("RELAY", loc='right', fontsize=9, color='green')
	elif direct_online and not relay_online:
		ax2.set_title("DIRECT", loc='right', fontsize=9, color='blue')
	elif direct_online and relay_online:
		if data_relay_time > data_time:
			use_relay = True
		ax2.set_title("RELAY&DIRECT ONLINE", loc='right', fontsize=9, color='green')

	usingdata = data_relay if use_relay else data

	if len(usingdata['rudder']) < 6:
		return

	x = usingdata['rudder'] 
	y = usingdata['elevator']
	xt = usingdata['rudder_trim']
	yt = usingdata['elevator_trim']
	spd = usingdata['airspeed']

	
	timestr = time.strftime("%H:%M:%S")
	ax1.set_title(timestr, loc='right', fontsize=9)

	ax2title = "csv"+str(len(x))+ ("r" if use_relay else "d")
	ax2.set_title(ax2title, loc='left',  fontsize=7)


	try:
		#last two datas
		xval = x[-1:].astype(float)
		yval = y[-1:].astype(float)
		#-5 to -1 datas
		xval_o = x[-5:].astype(float)
		yval_o = y[-5:].astype(float)
		#trim
		xval_t = xt[-1:].astype(float)
		yval_t = yt[-1:].astype(float)
		spdval = float(spd.iloc[-1])
	except ValueError as e:
		#たまに壊れたデータがここまできてしまうので、ここでExceptする。
		print(usingdata[-1:])
		print ('Value Error')
		return
	
	# max spd 更新
	if(spdval > maxspdval):
		maxspdval = spdval

	ln.set_data(xval, yval)
	ln2.set_data(xval_o, yval_o)
	ln3.set_data(xval_t, yval_t)

	for i, b in enumerate(barcollection):
		#print(i,spdval,maxspdval)
		if i == 0:
			b.set_width(spdval)
		elif i == 1:
			b.set_width(maxspdval)

	duration_in_s = (datetime.now()-timebegin).total_seconds() 
	print(" "+str(frame)+": {:.1f}ms".format(duration_in_s*1000),end="\r")
	
	#plt.tight_layout()

	return ln,ln2,ln3,barcollection[0],barcollection[1]


ani = FuncAnimation(plt.gcf(), animate, init_func=init, interval=DRAW_INTERVAL, cache_frame_data=False, blit=False)
plt.show()
