import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

columny = 'watts'
columnx = 'airspeed'

# Read the input CSV file
df = pd.read_csv('./csv/alba2024pilotlog_airspeed_added.csv')

# Filter data between time 380 and 1000
filtered_df = df[(df['time'] >= 380) & (df['time'] <= 1000)]

# Group by 20-second intervals and calculate the mean for each group
filtered_df['time_group'] = (filtered_df['time'] // 15) * 15
grouped_df = filtered_df.groupby('time_group').mean().reset_index()

# Normalize the time column for color mapping
norm = plt.Normalize(grouped_df['time_group'].min(), grouped_df['time_group'].max())
cmap = plt.get_cmap('viridis')

# Create scatter plot with gradient color based on time
plt.figure(figsize=(10, 6))
scatter = plt.scatter(grouped_df[columnx], grouped_df[columny], 
                      c=grouped_df['time_group'], cmap=cmap, norm=norm, label='Data Points')

# Add a color bar
cbar = plt.colorbar(scatter)
cbar.set_label('Time (s)')

# Define the modified power model with a smoother spike near the stall speed
def power_model_with_smooth_spike(V, a, b, c):
    stall_speed = 5.5
    min_drag_speed = 6.1
    if V <= stall_speed:
        return c * np.exp(-0.5 * (V - min_drag_speed))  # Smoother spike near stall speed
    elif stall_speed < V <= min_drag_speed:
        ratio = (V-stall_speed)/(min_drag_speed-stall_speed)
        return (a * (1 / V) + b * (V**3))*ratio + (1-ratio)* c*np.exp(-0.5 * (V - min_drag_speed))
    else:
        return a * (1 / V) + b * (V**3)

# Extract the x (airspeed) and y (watts) values
x_data = grouped_df[columnx]
y_data = grouped_df[columny]

# Apply the model to fit the data, including the smoother spike at stall speed
def piecewise_power_model(V, a, b, c):
    return np.array([power_model_with_smooth_spike(v, a, b, c) for v in V])

# Fit the data to the piecewise model using curve_fit
params, _ = curve_fit(piecewise_power_model, x_data, y_data, p0=[1, 1e-4, 500])  # Initial guesses for 'a', 'b', 'c'
a_fit, b_fit, c_fit = params
a_fit = 700
b_fit = 0.42
c_fit = 230

# Generate x values for plotting the fit line
x_range = np.linspace(5.5, 8.5, 100)  # Avoid division by zero
y_fit = piecewise_power_model(x_range, a_fit, b_fit, c_fit)

# Plot the fit line
plt.plot(x_range, y_fit, color='red', label=f'Fit Line: Spike near Stall and P = a*(1/V) + b*V^3')

# Add maximum L/D line (tangent to the fit line at minimum drag speed)
x_range = np.linspace(0, 8.5, 100)  # Avoid division by zero
max_ld_slope = 0.998*(a_fit / 6.2 + b_fit * 6.2 ** 3) / 6.2  # Slope of tangent at V = 6.2 m/s
y_ld = max_ld_slope * x_range  # Line crossing through (0,0)
plt.plot(x_range, y_ld, '--', color='blue', label='Max L/D Line (Tangent)')

# Set x-axis and y-axis limits
plt.xlim(0, 8.5)
plt.ylim(0, 350)

# Add labels and title
plt.xlabel(columnx)
plt.ylabel(columny)
plt.title(f'Scatter Plot ({columnx} vs. {columny}) with Power Spike near Stall Speed (Avg.15sec)')

# Add equation text with actual a and b values
equation_text = f'$P = {a_fit:.2f}*(1/V) + {b_fit:.2f}*V^3$'
plt.text(0.05, 0.95, equation_text, transform=plt.gca().transAxes, 
         fontsize=12, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

plt.legend()
plt.grid(True)

# Show plot
plt.show()