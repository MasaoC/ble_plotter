
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

columny = 'watts'
columnx = 'airspeed'

# Read the input CSV file
df = pd.read_csv('./csv/alba2024pilotlog_airspeed_added.csv')

# Filter data between time 380 and 1000
filtered_df = df[(df['time'] >= 380) & (df['time'] <= 1000)]

# Group by 10-second intervals and calculate the mean for each group
filtered_df['time_group'] = (filtered_df['time'] // 10) * 10
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

# Fit a second-degree polynomial to the data
coefficients = np.polyfit(grouped_df[columnx], grouped_df[columny], 2)
polynomial = np.poly1d(coefficients)
x_range = np.linspace(grouped_df[columnx].min(), grouped_df[columnx].max(), 100)
y_trend = polynomial(x_range)

# Plot trend line
plt.plot(x_range, y_trend, color='red', label='Trend Line')

# Label the equation on the plot
equation_text = f'$y = {coefficients[0]:.2e}x^2 + {coefficients[1]:.2f}x + {coefficients[2]:.2f}$'
plt.text(0.05, 0.95, equation_text, transform=plt.gca().transAxes, 
         fontsize=12, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

# Add labels and title
plt.xlabel(columnx)
plt.ylabel(columny)
plt.title('Scatter Plot ('+columnx+' vs. '+columny+') Averaged Over 10-Second Intervals with Trend Line')
plt.legend()
plt.grid(True)

# Show plot
plt.show()

