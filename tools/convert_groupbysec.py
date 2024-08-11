import pandas as pd

# Read the input CSV file
df = pd.read_csv('./csv/log2024.csv')

# Convert '経過時間(ms)' to seconds and round to the nearest integer
df['time'] = (df['経過時間(ms)'] / 1000).round().astype(int)

# Group by the new 'time' column and calculate the average of '速度(m/s)' and '水平舵角'
result_df = df.groupby('time', as_index=False).agg({'速度(m/s)': 'mean', '水平舵角': 'mean'})

# Save the result to a new CSV file
result_df.to_csv('output.csv', index=False, header=['time', '速度(m/s)', '水平舵角'])
