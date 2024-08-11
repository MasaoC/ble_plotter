import pandas as pd
import matplotlib.pyplot as plt

# Read the input CSV file
df = pd.read_csv('./csv/alba2024pilotlog_airspeed_added.csv')

# Create a figure and axis
fig, ax1 = plt.subplots()

# Plot watts on the primary y-axis
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Watts', color='tab:blue')
ax1.plot(df['time'], df['watts'], color='tab:blue', label='Watts')
ax1.tick_params(axis='y', labelcolor='tab:blue')

# Create a second y-axis for airspeed
ax2 = ax1.twinx()  
ax2.set_ylabel('Airspeed (m/s)', color='tab:green')  
ax2.plot(df['time'], df['airspeed'], color='tab:green', label='Airspeed')
ax2.tick_params(axis='y', labelcolor='tab:green')

# Add a title and show the plot
plt.title('Watts and Airspeed vs. Time')
fig.tight_layout()  # Adjust layout to fit the labels
plt.show()