import pandas as pd
import numpy as np
import glob
import os

# 1. Define the Lat/Lon for your 12 stations
stations_coords = {
    'Aotizhongxin': {'lat': 39.982, 'lon': 116.397},
    'Changping': {'lat': 40.217, 'lon': 116.230},
    'Dingling': {'lat': 40.292, 'lon': 116.220},
    'Dongsi': {'lat': 39.929, 'lon': 116.417},
    'Guanyuan': {'lat': 39.929, 'lon': 116.339},
    'Gucheng': {'lat': 39.914, 'lon': 116.184},
    'Huairou': {'lat': 40.328, 'lon': 116.628},
    'Nongzhanguan': {'lat': 39.937, 'lon': 116.461},
    'Shunyi': {'lat': 40.127, 'lon': 116.655},
    'Tiantan': {'lat': 39.886, 'lon': 116.407},
    'Wanliu': {'lat': 39.987, 'lon': 116.287},
    'Wanshouxigong': {'lat': 39.878, 'lon': 116.352}
}

# 2. Assign Spatial Characteristics (The "Teaching" Data)
# Since we are using Belgium shapefiles for the APP, we simulate these 
# distances for the Beijing TRAINING so the model learns the relationship.
# Higher dist_to_highway = Lower PM2.5
spatial_profiles = {
    'Aotizhongxin': {'dist_to_highway': 50, 'dist_to_industrial': 5000, 'dist_to_water': 1200},
    'Dingling': {'dist_to_highway': 2000, 'dist_to_industrial': 15000, 'dist_to_water': 500},
    # ... (Model learns that Dingling is cleaner because distances are higher)
}

# Default values for stations not in the profile
default_profile = {'dist_to_highway': 500, 'dist_to_industrial': 3000, 'dist_to_water': 2000}

# 3. Process the CSVs
csv_files = glob.glob("PRSA_Data_*.csv")

for file in csv_files:
    df = pd.read_csv(file)
    station_name = df['station'].iloc[0]
    
    # Map the spatial data
    profile = spatial_profiles.get(station_name, default_profile)
    
    df['dist_to_highway'] = profile['dist_to_highway']
    df['dist_to_industrial'] = profile['dist_to_industrial']
    df['dist_to_water'] = profile['dist_to_water']
    
    # Save the new "Enriched" CSV
    new_filename = f"ENRICHED_{file}"
    df.to_csv(new_filename, index=False)
    print(f"✅ Created: {new_filename}")
    