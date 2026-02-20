from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
from datetime import datetime

# Initialize App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the AI Brain (0.95 Accuracy Model)
model = joblib.load('air_quality_model.pkl')
model_features = joblib.load('model_features.pkl')

# Load Belgium Spatial Layers
print("🌍 Connecting Environmental GIS Layers...")
roads = gpd.read_file('spatial_data/gis_osm_roads_free_1.shp').to_crs(epsg=3857)
landuse = gpd.read_file('spatial_data/gis_osm_landuse_a_free_1.shp').to_crs(epsg=3857)
natural = gpd.read_file('spatial_data/gis_osm_natural_a_free_1.shp').to_crs(epsg=3857)

# Pre-calculate to keep map clicks fast
traffic = roads[roads['fclass'].isin(['motorway', 'trunk', 'primary'])].union_all()
industry = landuse[landuse['fclass'] == 'industrial'].union_all()
forest = natural[natural['fclass'].isin(['forest', 'park', 'wood'])].union_all()
print("✅ Hyper-Local Layers Ready.")

class PredictionRequest(BaseModel):
    lat: float; lon: float; temp: float; pres: float; dewp: float; rain: float; wspm: float; pm25_lag_1: float

@app.post("/predict")
async def predict(req: PredictionRequest):
    try:
        # Spatial pinpointing logic
        user_p = gpd.GeoSeries([Point(req.lon, req.lat)], crs="EPSG:4326").to_crs(epsg=3857).iloc[0]
        search_area = user_p.buffer(2000) # Only check within 2km
        
        def get_dist(union):
            if not union: return 5000.0
            local = union.intersection(search_area)
            return float(user_p.distance(local)) if not local.is_empty else 2000.0

        spatial = {
            'dist_traffic': get_dist(traffic),
            'dist_industrial': get_dist(industry),
            'dist_forest': get_dist(forest),
            'dist_urban': 500.0,
            'dist_water': 1200.0
        }

        # Combine REAL weather with SPATIAL distances
        input_data = {
            **spatial,
            'TEMP': req.temp, 'PRES': req.pres, 'DEWP': req.dewp,
            'RAIN': req.rain, 'WSPM': req.wspm, 'pm25_lag_1': req.pm25_lag_1,
            'hour_sin': np.sin(2 * np.pi * datetime.now().hour / 24),
            'hour_cos': np.cos(2 * np.pi * datetime.now().hour / 24)
        }

        # Model Inference
        input_df = pd.DataFrame([input_data]).reindex(columns=model_features, fill_value=0)
        prediction = float(model.predict(input_df)[0])
        
        return {
            "pm25": round(prediction, 2),
            "status": "Good" if prediction < 35 else "Moderate" if prediction < 75 else "Unhealthy",
            "report": {k: round(v, 1) for k, v in spatial.items()}
        }
    except Exception as e:
        return {"error": str(e)}