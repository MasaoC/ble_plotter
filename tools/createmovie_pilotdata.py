import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from matplotlib.animation import ArtistAnimation
import matplotlib.patheffects as path_effects

FILENAME = './csv/pilotdata2024.csv'
SAVENAME = 'pilotdata2024.mp4'
start = 308#508 #308
stop = 1030#530 #1030

# データの読み込み
data = pd.read_csv(FILENAME)
time = data['time'].values
spd = data['velocity_smooth'].values
watts = data['watts'].values
cadence = data['cadence'].values
distance = data['distance'].values

# 線形補間を行うための時間配列
frame_interval = 1
new_time = np.arange(start, stop, frame_interval)

# 線形補間
interp_func_spd = interp1d(time, spd, kind='linear')
new_spd = interp_func_spd(new_time)

interp_func_watts = interp1d(time, watts, kind='linear')
new_watts = interp_func_watts(new_time)

interp_func_cadence = interp1d(time, cadence, kind='linear')
new_cadence = interp_func_cadence(new_time)

interp_func_distance = interp1d(time, distance, kind='linear')
new_distance = interp_func_distance(new_time)

# グラフを表示する領域を，figオブジェクトとして作成
fig, (ax2, ax3, ax1,tt_ax) = plt.subplots(4, 1, figsize=(5, 5), facecolor='green', gridspec_kw={'height_ratios': [0.5, 0.5, 0.5, 2]})

# 風速表示
tt_ax.set_xlim(-1, 1)
tt_ax.set_ylim(-1, 1)
tt_ax.set_facecolor('green')
tt_ax.grid(False)
tt_ax.xaxis.set_visible(False)
tt_ax.yaxis.set_visible(False)
for spine in tt_ax.spines.values():
    spine.set_visible(False)

# グラフ設定
ax1.grid(axis='x')
ax1.set_xlim(0, 10)
ax1.set_xticks(range(11))
ax1.set_facecolor('lightgreen')

ax2.grid(axis='x')
ax2.set_xlim(150, 400)
ax2.set_facecolor('lightgreen')

ax3.grid(axis='x')
ax3.set_xlim(60, 120)
ax3.set_facecolor('lightgreen')

plt.tight_layout()

frames = []
for i in range(len(new_time)):
    # Create text for each frame
    lat_text = tt_ax.text(0.5, 0.7, f"P Lat: {data['lat'].iloc[i]:.6f}", horizontalalignment='center', verticalalignment='center', transform=tt_ax.transAxes, color='black', fontsize=15, fontweight='bold', path_effects=[path_effects.withStroke(linewidth=3, foreground='white')])
    lon_text = tt_ax.text(0.5, 0.55 , f"P Lon: {data['lng'].iloc[i]:.6f}", horizontalalignment='center', verticalalignment='center', transform=tt_ax.transAxes, color='black', fontsize=15, fontweight='bold', path_effects=[path_effects.withStroke(linewidth=3, foreground='white')])
    dist_text = tt_ax.text(0.5, 1.0, f"Travel Dist: {new_distance[i]:.1f}m", horizontalalignment='center', verticalalignment='center', transform=tt_ax.transAxes, color='black', fontsize=20, fontweight='bold', path_effects=[path_effects.withStroke(linewidth=3, foreground='white')])
    time_text = tt_ax.text(0.5, 0.4, f"Time: {time[i]:.0f}s", horizontalalignment='center', verticalalignment='center', transform=tt_ax.transAxes, color='black', fontsize=10, fontweight='bold', path_effects=[path_effects.withStroke(linewidth=1, foreground='white')])

    frame1 = ax1.barh(" ", [new_spd[i]], height=0.05, color="black")
    frame2 = ax2.barh(' ', [new_watts[i]], height=0.05, color="blue")
    frame3 = ax3.barh(' ', [new_cadence[i]], height=0.05, color="blue")

    # Manually add text annotations with outlined effect
    spd_text = ax1.text(0, 0, f"PILOT G/S {new_spd[i]:.1f}m/s", va='center', ha='left', color='black', fontsize=18, fontweight='bold', path_effects=[path_effects.withStroke(linewidth=3, foreground='white')])
    watt_text = ax2.text(150, 0, f"WATT {new_watts[i]:.0f}", va='center', ha='left', color='black', fontsize=18, fontweight='bold', path_effects=[path_effects.withStroke(linewidth=3, foreground='white')])
    cadence_text = ax3.text(60, 0, f"CADENCE {new_cadence[i]:.0f}", va='center', ha='left', color='black', fontsize=18, fontweight='bold', path_effects=[path_effects.withStroke(linewidth=3, foreground='white')])

    # Append text objects to the frames list
    frames.append(tuple(frame1) + tuple(frame2) + tuple(frame3) + (lat_text, lon_text, dist_text, spd_text, watt_text, cadence_text,time_text))

ani = ArtistAnimation(fig, frames, interval=frame_interval*1000)

# アニメーションの保存
ani.save(SAVENAME, writer='ffmpeg', fps=1/frame_interval)
