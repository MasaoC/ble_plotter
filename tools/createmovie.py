import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from matplotlib.animation import ArtistAnimation
import time

# Start time measurement
start_time = time.time()

FILENAME = './csv/log2024.csv'
SAVENAME = '2024log.mp4'
start   = 3449831/1000
stop    = 4171380/1000
#4171381

# データの読み込み
data = pd.read_csv(FILENAME)
time = data['経過時間(ms)'].values/1000
roll = -data['roll'].values
pitch = data['pitch'].values  # rudderデータの読み込み
yaw = data['yaw'].values+360  # rudderデータの読み込み
spd = data['速度(m/s)'].values  # 
hei = data['高度(cm)'].values
elv = data['水平舵角'].values
rud = data['垂直舵角'].values
rud_trim = data['垂直トリム'].values
elv_trim = data['水平トリム'].values


frame_interval = 0.1

long = int(2 / frame_interval)

new_time = np.arange(start, stop, frame_interval)

# 線形補間を行う
interp_func_pitch = interp1d(time, pitch, kind='linear')
new_pitch = interp_func_pitch(new_time)

interp_func_roll = interp1d(time, roll, kind='linear')
new_roll = interp_func_roll(new_time)

interp_func_spd = interp1d(time, spd, kind='linear')
new_spd = interp_func_spd(new_time)

interp_func_yaw = interp1d(time, yaw, kind='linear')
new_yaw = interp_func_yaw(new_time)

interp_func_hei = interp1d(time, hei, kind='linear')
new_hei = interp_func_hei(new_time)

interp_func_elv = interp1d(time, elv, kind='linear')
new_elv = interp_func_elv(new_time)

interp_func_rud = interp1d(time, rud, kind='linear')
new_rud = interp_func_rud(new_time)


interp_func_elvtrim = interp1d(time, elv_trim, kind='linear')
new_elvtrim = interp_func_elvtrim(new_time)

interp_func_rudtrim = interp1d(time, rud_trim, kind='linear')
new_rudtrim = interp_func_rudtrim(new_time)

# グラフを表示する領域を，figオブジェクトとして作成．
fig, (ax1, axyaw, ax2, ax3) = plt.subplots(4, 1, figsize=(4, 6), facecolor='green',gridspec_kw={'height_ratios': [9, 0.5, 0.5, 0.5]})
# 風速表示


ax1.grid()
ax1.set_xlim(-15,15)
ax1.set_ylim(-10,6)
ax1.set_xlabel("LEFT   <-   ->   RIGHT")
ax1.set_ylabel("UP   <-   ->   DOWN")
ax1.plot([-20,20],[0,0],c='black')
ax1.plot([0,0],[-20,20],c='black')
ax1.invert_yaxis()
ax1.set_facecolor('lightgreen')

ax2.grid(axis = 'x')
ax2.set_xlim(0,10)
#ax2.xaxis.set_visible(False)
ax2.set_yticks([0], labels=["SPD"])
ax2.set_xticks(range(11))
ax2.set_facecolor('white')

axyaw.grid(axis = 'x')
axyaw.set_xlim(0,360)
#ax2.xaxis.set_visible(False)
axyaw.set_yticks([0], labels=["YAW"])
axyaw.set_facecolor('white')
axyaw.set_xticks([0,90,180,270,360])

ax3.grid(axis = 'x')
ax3.set_xlim(0,210)
#ax2.xaxis.set_visible(False)
ax3.set_yticks([0], labels=["HGT"])
#ax3.set_xticks([10,30,50,70,90,110,130,150,200])
ax3.set_facecolor('white')

ax1.text(0.5, 1.01, " ".format(new_yaw[0]), horizontalalignment='center', verticalalignment='bottom', transform=ax1.transAxes, fontsize="large")
ax1.text(0.5, 0.94, "Blue=(ELV,RUD). BLK=(-Pitch,Bank). RED=Trim", horizontalalignment='center', verticalalignment='bottom', transform=ax1.transAxes,fontsize="small")
plt.tight_layout()


frames = []
for i in range(len(new_time)):
    length = i
    tail = 0
    if i+1 > long:
        tail = i - long
        length = long
    frame3 = ax1.plot(new_roll[i], new_pitch[i] , color='black', marker='o',markersize=10, linewidth=0)
    frame4 = ax1.plot(new_roll[tail:tail+length+1],new_pitch[tail:tail+length+1],c='black',linewidth=3,alpha=0.5)

   
    frame5 = ax2.barh('SPD',[new_spd[i]], height =[0.1],  color=["blue"])
    frame6 = ax3.barh('HGT',[new_hei[i]], height =[0.1],  color=["blue"])

    frame7 = ax1.plot(new_rud[i], new_elv[i] , color='blue', marker='o',markersize=15, linewidth=0,alpha=0.8)
    frame8 = ax1.plot(new_rud[tail:tail+length+1],new_elv[tail:tail+length+1],c='blue',linewidth=3,alpha=0.5)

    frame9 = axyaw.barh('YAW',[new_yaw[i]], height =[0.1],  color=["black"])
    
    frame10= ax1.plot(new_rudtrim[i], new_elvtrim[i] , color='red', marker='.',markersize=10, linewidth=0)
    
    #ttl = ax1.text(0.5, 1.01, "YAW{0:.1f}".format(new_yaw[i]), horizontalalignment='center', verticalalignment='bottom',  transform=ax1.transAxes, fontsize="large")

    frames.append(frame3+frame10+frame4+frame7+frame8+list(frame9)+list(frame5)+list(frame6))

ani = ArtistAnimation(fig, frames, interval=frame_interval*1000)

# アニメーションの保存
ani.save(SAVENAME, writer='ffmpeg', fps=1/frame_interval)

import time
# End time measurement and print elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")

