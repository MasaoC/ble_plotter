

'''
    File name: plotter.py
    Author: Masao Chiguchi
    Date created: 2024/05/26
    Date last modified: 2024/5/28
    Python Version: 3.10.0 (tested on)

	CSVファイルを開き、グラフ化する
	最新のCSVファイル名は「setting_plotter.txt」から読み込む。
'''

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
import time
from datetime import datetime
import random


settingf = open("setting_plotter.txt", "r")
csvfilename = settingf.readline()
graph_title = csvfilename.replace(".csv", "").replace("csv","")
print(csvfilename)

matplotlib.rcParams['toolbar'] = 'None'

# グラフを表示する領域を，figオブジェクトとして作成．
fig, (ax1,ax2) = plt.subplots(1, 2, figsize=(5,4), facecolor='lightblue',gridspec_kw={'width_ratios': [6, 1]})




maxspdval = 0
barcollection = ax2.bar([0,1],[0,maxspdval],width=[1,0.3], color=["blue","aqua"])


# Animation requirements.
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
	ax1.set_ylim(-6,6)
	ax1.set_title(graph_title)
	ax2.grid(axis = 'y')
	ax2.set_ylim(0,10)
	#ax2.xaxis.set_visible(False)
	ax2.set_xticks([0,1], labels=["SPD","Max"])
	ax2.set_yticks(range(11))

	return ln,


def barlist(n): 
    return [1/float(n*k) for k in range(1,6)]

def animate(frame):
	global maxspdval
	timebegin = datetime.now()
	data = pd.read_csv("./csv/"+csvfilename)
	data.apply(pd.to_numeric, errors='coerce')


	x = data['rudder']
	y = data['elevator']
	xt = data['rudder_trim']
	yt = data['elevator_trim']
	spd = data['airspeed']

	
	timestr = time.strftime("%H:%M:%S(")+str(len(x))+")"
	ax2.set_title(timestr, y=1.05, fontsize=9)

	if(len(x) < 6):
		return
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
	if(spdval > maxspdval):
		maxspdval = spdval
	#print (xval,yval,xval_o,yval_o)
	ln.set_data(xval, yval)
	ln2.set_data(xval_o, yval_o)
	ln3.set_data(xval_t, yval_t)

	for i, b in enumerate(barcollection):
		#print(i,spdval,maxspdval)
		if i == 0:
			b.set_height(spdval)
		elif i == 1:
			b.set_height(maxspdval)

	duration_in_s = (datetime.now()-timebegin).total_seconds() 
	print(" "+str(frame)+": {:.1f}ms".format(duration_in_s*1000),end="\r")
	return ln,ln2,ln3,barcollection[0],barcollection[1]


ani = FuncAnimation(plt.gcf(), animate, init_func=init, interval=66, cache_frame_data=False, blit=False)
plt.show()
