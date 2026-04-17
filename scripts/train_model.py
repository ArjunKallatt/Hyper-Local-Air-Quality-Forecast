import pandas as pd
import numpy as np
import glob
import joblib
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import r2_score

# 1. STATION COORDINATES (The "Secret Sauce")
# These are the real lat/lon for the 12 Beijing stations in your dataset
STATION_COORDS = {
    'Aotizhongxin': [39.982, 116.397], 'Changping': [40.217, 116.230],
    'Dingling': [40.292, 116.220], 'Dongsi': [39.929, 116.417],
    'Guanyuan': [39.929, 116.339], 'Gucheng': [39.914, 116.184],
    'Huairou': [40.328, 116.628], 'Nongzhanguan': [39.937, 116.461],
    'Shunyi': [40.127, 116.655], 'Tiantan': [39.886, 116.407],
    'Wanliu': [39.987, 116.287], 'Wanshouxigong': [39.878, 116.352]
}

# 2. SIMULATED ENVIRONMENTAL DISTANCES (Since Beijing shapefiles vary)
# This "teaches" the model how distance affects PM2.5 based on station location
STATION_FEATURES = {
    'Aotizhongxin': {'dist_traffic': 150, 'dist_industrial': 5000, 'dist_urban': 200, 'dist_forest': 800, 'dist_water': 1200},
    'Dingling': {'dist_traffic': 3000, 'dist_industrial': 15000, 'dist_urban': 5000, 'dist_forest': 50, 'dist_water': 500},
    # Add logic: Urban stations (Dongsi) are close to traffic, Rural (Huairou) are close to forest.
}

def load_data():
    all_files = glob.glob("/home/aaru/projects/Hyper Local Air Quality Forcast/data/datasets/PRSA_Data_*.csv")
    df_list = []
    
    for filename in all_files:
        station_name = filename.split('_')[2]
        df = pd.read_csv(filename)
        
        # A. Add Spatial Features to the CSV
        feat = STATION_FEATURES.get(station_name, STATION_FEATURES['Aotizhongxin'])
        for col, val in feat.items():
            df[col] = val
            
        df_list.append(df)
    
    return pd.concat(df_list, axis=0)

# 3. PREPROCESSING
df = load_data()
df = df.dropna(subset=['PM2.5'])
df['pm25_lag_1'] = df.groupby('station')['PM2.5'].shift(1)
df = df.dropna()

# Create Time Features
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

# 4. TRAINING
features = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM', 'pm25_lag_1', 
            'hour_sin', 'hour_cos', 'dist_traffic', 'dist_industrial', 
            'dist_urban', 'dist_forest', 'dist_water']

X = df[features]
y = df['PM2.5']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("🚀 Training Hyper-Local XGBoost Model...")
model = xgb.XGBRegressor(n_estimators=1000, max_depth=7, learning_rate=0.05, subsample=0.8)
model.fit(X_train, y_train)

# 5. SAVE & VALIDATE
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print(f"✅ Training Complete! R^2 Score: {r2_score(y_test, y_pred):.4f}")
print(f"R2 Score: {r2_score(y_test, y_pred):.4f}")
print(f"MAE (Mean Absolute Error): {mae:.2f}")
print(f"MSE (Mean Squared Error): {mse:.2f}")
print(f"RMSE (Root Mean Squared Error): {rmse:.2f}")
joblib.dump(model, 'air_quality_model.pkl')
joblib.dump(features, 'model_features.pkl')
print("📦 Model and Features saved to /backend")
