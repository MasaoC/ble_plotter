'''
    File name: plotter.py
    Author: Masao Chiguchi
    Date created: 2024/05/26
    Date last modified: 2024/05/28
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
import os.path
from collections import deque

class bcolors:
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

DRAW_INTERVAL = 100  # 100ms = 10Hz
disable_relay = False
AIRSPEED_WINDOW_SECONDS = 10  # Show last 10 seconds of airspeed data
airspeed_buffer = deque(maxlen=int(AIRSPEED_WINDOW_SECONDS * 1000 / DRAW_INTERVAL))  # Buffer for ~100 points at 10Hz

# Check if settings file exists
if not os.path.isfile("setting_plotter.txt"):
    print(bcolors.FAIL + bcolors.BOLD + "Warning: setting_plotter.txt not found." + bcolors.ENDC)
    print("Check 'python ble.py' is running")
    exit(0)

# Read settings file
with open("setting_plotter.txt", "r") as settingf:
    csvfilename = settingf.readline().rstrip('\n')
    csvfilename_relay = settingf.readline().rstrip('\n')

# Check if relay file is specified and exists
if not csvfilename_relay or not os.path.isfile(f"./csv/{csvfilename_relay}"):
    disable_relay = True

graph_title = csvfilename.replace(".csv", "").replace("csv", "")

print(f"Using CSV: {csvfilename}")
if not disable_relay:
    print(f"Using Relay CSV: {csvfilename_relay}")

# Disable toolbar
matplotlib.rcParams['toolbar'] = 'None'

# Create figure with three subplots (6:1:3 ratio for rudder/elevator : airspeed bar : airspeed time-series)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(4, 7), facecolor='lightblue', 
                                    gridspec_kw={'height_ratios': [6, 1, 3]})

# Maximum airspeed tracker
maxspdval = 0

# Airspeed bar plot
barcollection = ax2.barh([0, 1], [0, maxspdval], height=[1, 0.3], color=["blue", "aqua"])

# Plot lines for rudder/elevator, history, and trim
ln, = ax1.plot([], [], color='blue', marker='o', linewidth=1, markersize=7, alpha=1)
ln2, = ax1.plot([], [], color='blue', marker='o', linewidth=1, markersize=2, alpha=0.5)
ln3, = ax1.plot([], [], color='red', marker='o', linewidth=1, markersize=5, alpha=0.5)

# Airspeed time-series plot
ln_airspeed, = ax3.plot([], [], color='green', linewidth=2)

def init():
    ax1.set_xlabel("LEFT   <-   ->   RIGHT")
    ax1.set_ylabel("UP   <-   ->   DOWN")
    ax1.plot([-20, 20], [0, 0], c='black')  # Horizontal axis
    ax1.plot([0, 0], [-20, 20], c='black')  # Vertical axis
    ax1.grid()
    ax1.set_xlim(-16, 16)
    ax1.set_ylim(-8, 8)
    ax1.set_title(graph_title)
    ax1.invert_yaxis()

    ax2.grid(axis='x')
    ax2.set_xlim(0, 10)
    ax2.invert_yaxis()
    ax2.set_yticks([0, 1], labels=["SPD", "Max"])
    ax2.set_xticks(range(11))

    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("Airspeed")
    ax3.grid()
    ax3.set_xlim(-AIRSPEED_WINDOW_SECONDS, 0)
    ax3.set_ylim(0, 10)  # Adjust based on expected airspeed range
    ax3.set_title("Airspeed Over Time")

    plt.tight_layout()

    return ln, ln2, ln3, barcollection[0], barcollection[1], ln_airspeed

def animate(frame):
    global maxspdval, disable_relay
    timebegin = datetime.now()

    try:
        # Read only the last 6 rows of primary CSV
        data = pd.read_csv(f"./csv/{csvfilename}").tail(6)
        numeric_columns = ['rudder', 'elevator', 'rudder_trim', 'elevator_trim', 'airspeed']
        data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')

        # Read only the last 6 rows of relay CSV if enabled
        data_relay = None
        if not disable_relay:
            try:
                data_relay = pd.read_csv(f"./csv/{csvfilename_relay}").tail(6)
                data_relay[numeric_columns] = data_relay[numeric_columns].apply(pd.to_numeric, errors='coerce')
            except FileNotFoundError:
                print(f"Relay file {csvfilename_relay} not found, disabling relay")
                disable_relay = True

        data_time, data_relay_time = None, None
        direct_online, relay_online = False, False
        use_relay = False

        # Check if data is recent and frequent enough (2.5Hz, 3s window)
        if len(data['time']) >= 6:
            try:
                data_time = datetime.strptime(data['time'].iloc[-1], '%Y-%m-%d %H:%M:%S.%f')
                data_time_5 = datetime.strptime(data['time'].iloc[-5], '%Y-%m-%d %H:%M:%S.%f')
                direct_online = (datetime.now() - data_time).total_seconds() < 3 and \
                                (data_time - data_time_5).total_seconds() < 2
            except (ValueError, TypeError) as e:
                print(f"Time parsing error (direct): {e}")
                direct_online = False

        if not disable_relay and data_relay is not None and len(data_relay['time']) >= 6:
            try:
                data_relay_time = datetime.strptime(data_relay['time'].iloc[-1], '%Y-%m-%d %H:%M:%S.%f')
                data_relay_time_5 = datetime.strptime(data_relay['time'].iloc[-5], '%Y-%m-%d %H:%M:%S.%f')
                relay_online = (datetime.now() - data_relay_time).total_seconds() < 3 and \
                               (data_relay_time - data_relay_time_5).total_seconds() < 2
            except (ValueError, TypeError) as e:
                print(f"Time parsing error (relay): {e}")
                relay_online = False

        # Determine connection status
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

        # Select data source
        usingdata = data_relay if use_relay and not disable_relay else data

        if len(usingdata['rudder']) < 6:
            return

        # Extract data
        x = usingdata['rudder']
        y = usingdata['elevator']
        xt = usingdata['rudder_trim']
        yt = usingdata['elevator_trim']
        spd = usingdata['airspeed']

        timestr = time.strftime("%H:%M:%S")
        ax1.set_title(timestr, loc='right', fontsize=9)

        ax2title = f"csv{len(x)}{'r' if use_relay else 'd'}"
        ax2.set_title(ax2title, loc='left', fontsize=7)

        # Extract last values
        try:
            xval = x.iloc[-1:].astype(float)
            yval = y.iloc[-1:].astype(float)
            xval_o = x.iloc[-5:].astype(float)
            yval_o = y.iloc[-5:].astype(float)
            xval_t = xt.iloc[-1:].astype(float)
            yval_t = yt.iloc[-1:].astype(float)
            spdval = float(spd.iloc[-1])
            current_time = datetime.strptime(usingdata['time'].iloc[-1], '%Y-%m-%d %H:%M:%S.%f')
        except (ValueError, TypeError) as e:
            print(f"Data error: {e}")
            print(usingdata.iloc[-1:])
            return

        # Update airspeed buffer
        airspeed_buffer.append((current_time, spdval))

        # Update max speed
        if spdval > maxspdval:
            maxspdval = spdval

        # Update rudder/elevator plots
        ln.set_data(xval, yval)
        ln2.set_data(xval_o, yval_o)
        ln3.set_data(xval_t, yval_t)

        # Update airspeed bar
        for i, b in enumerate(barcollection):
            if i == 0:
                b.set_width(spdval)
            elif i == 1:
                b.set_width(maxspdval)

        # Update airspeed time-series plot
        if airspeed_buffer:
            times, speeds = zip(*airspeed_buffer)
            # Convert times to seconds relative to the latest time
            latest_time = times[-1]
            relative_times = [(t - latest_time).total_seconds() for t in times]
            # Filter data to last 10 seconds
            valid_indices = [i for i, t in enumerate(relative_times) if -AIRSPEED_WINDOW_SECONDS <= t <= 0]
            relative_times = [relative_times[i] for i in valid_indices]
            speeds = [speeds[i] for i in valid_indices]
            ln_airspeed.set_data(relative_times, speeds)
            # Adjust y-axis dynamically
            if speeds:
                ax3.set_ylim(0, 10)

        duration_in_s = (datetime.now() - timebegin).total_seconds()
        print(f" {frame}: {duration_in_s*1000:.1f}ms", end="\r")

        return ln, ln2, ln3, barcollection[0], barcollection[1], ln_airspeed

    except Exception as e:
        print(f"Error in animate: {e}")
        return

ani = FuncAnimation(plt.gcf(), animate, init_func=init, interval=DRAW_INTERVAL, cache_frame_data=False, blit=False)
plt.show()