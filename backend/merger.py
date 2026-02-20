import pandas as pd
import glob
import numpy as np

# Find all CSV files in your folder
path = './' # adjust this to your folder path
all_files = glob.glob(path + "PRSA_Data_*.csv")

# Read and combine them
li = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

# This is your single master dataframe
master_df = pd.concat(li, axis=0, ignore_index=True)

print(f"Combined {len(all_files)} files into {master_df.shape[0]} rows.")

# Save the combined data to a new CSV file
master_df.to_csv('Beijing_AirQuality_Master.csv', index=False)

print("Success! Your new file 'Beijing_AirQuality_Master.csv' has been created.")

# Identify columns with missing values (PM2.5, TEMP, etc.)
cols_to_fix = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']

# Use linear interpolation to fill gaps
# 'limit_direction' ensures it fills both forwards and backwards
master_df[cols_to_fix] = master_df[cols_to_fix].interpolate(method='linear', limit_direction='both')

# Check if any NaNs remain
print(master_df.isnull().sum())

# 1. Create a datetime column for easier manipulation
master_df['datetime'] = pd.to_datetime(master_df[['year', 'month', 'day', 'hour']])

# 2. Cyclical Hour (24-hour cycle)
master_df['hour_sin'] = np.sin(2 * np.pi * master_df['hour'] / 24)
master_df['hour_cos'] = np.cos(2 * np.pi * master_df['hour'] / 24)

# 3. Cyclical Month (12-month cycle)
master_df['month_sin'] = np.sin(2 * np.pi * master_df['month'] / 12)
master_df['month_cos'] = np.cos(2 * np.pi * master_df['month'] / 12)

# Now you can drop the original 'hour' and 'month' columns if you wish
# as the Sin/Cos versions represent the patterns better for XGBoost.