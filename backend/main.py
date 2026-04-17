from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import math
from datetime import datetime

app = FastAPI(title="India Air Pinpoint API")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

try:
    model = joblib.load('air_quality_model.pkl')
    model_features = joblib.load('model_features.pkl')
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")

try:
    print("Loading roads (filtered)...")
    roads = gpd.read_file(
        'spatial_data/gis_osm_roads_free_1.shp',
        where="fclass IN ('motorway', 'trunk', 'primary')"
    ).to_crs(epsg=3857)
    traffic_layer = roads
    _ = traffic_layer.sindex
    print(f"Roads loaded: {len(roads)} features")

    print("Loading landuse (filtered)...")
    landuse = gpd.read_file(
        'spatial_data/gis_osm_landuse_a_free_1.shp',
        where="fclass = 'industrial'"
    ).to_crs(epsg=3857)
    industry_layer = landuse
    _ = industry_layer.sindex
    print(f"Landuse loaded: {len(landuse)} features")

    print("Loading natural (filtered)...")
    natural = gpd.read_file(
        'spatial_data/gis_osm_natural_a_free_1.shp',
        where="fclass IN ('forest', 'park', 'wood')"
    ).to_crs(epsg=3857)
    forest_layer = natural
    _ = forest_layer.sindex
    print(f"Natural loaded: {len(natural)} features")

except Exception as e:
    print(f"GIS Loading Error: {e}")
    traffic_layer = gpd.GeoDataFrame()
    industry_layer = gpd.GeoDataFrame()
    forest_layer = gpd.GeoDataFrame()


class PredictionRequest(BaseModel):
    lat: float
    lon: float
    temp: float
    pres: float
    dewp: float
    rain: float
    wspm: float
    pm25_lag_1: float


@app.post("/predict")
async def predict(req: PredictionRequest):
    try:
        user_p = Point(req.lon, req.lat)
        user_gdf = gpd.GeoSeries([user_p], crs="EPSG:4326").to_crs(epsg=3857)
        user_p_proj = user_gdf.iloc[0]

        def get_fast_dist(layer, max_dist=200000.0):
            if layer.empty:
                return 200000.0
            possible_matches_index = layer.sindex.query(user_p_proj.buffer(max_dist), predicate="intersects")
            if len(possible_matches_index) == 0:
                return 200000.0
            matches = layer.iloc[possible_matches_index]
            return float(matches.distance(user_p_proj).min())

        spatial = {
            'dist_traffic':    get_fast_dist(traffic_layer),
            'dist_industrial': get_fast_dist(industry_layer),
            'dist_forest':     get_fast_dist(forest_layer),
            'dist_urban':  500.0,
            'dist_water': 1200.0
        }

        # Detect missing shapefile coverage
        NO_DATA = 190000.0
        using_fallback = spatial['dist_traffic'] > NO_DATA

        if using_fallback:
            urban_score = max(0, min(1, (1020 - req.pres) / 20.0))
            spatial['dist_traffic']    = 50  + (1 - urban_score) * 800
            spatial['dist_industrial'] = 200 + (1 - urban_score) * 2000
            spatial['dist_forest']     = 2000 + (1 - urban_score) * 5000

        input_data = {
            **spatial,
            'TEMP': req.temp,
            'PRES': req.pres,
            'DEWP': req.dewp,
            'RAIN': req.rain,
            'WSPM': req.wspm,
            'pm25_lag_1': req.pm25_lag_1,
            'hour_sin': np.sin(2 * np.pi * datetime.now().hour / 24),
            'hour_cos': np.cos(2 * np.pi * datetime.now().hour / 24)
        }

        input_df = pd.DataFrame([input_data]).reindex(columns=model_features, fill_value=0)
        raw_prediction = float(model.predict(input_df)[0])

        # Weather factor — trust the ML model more directly
        weather_factor = (raw_prediction - 15.0) / 185.0
        weather_factor = max(0, min(1, weather_factor))

        # Meteorological signals
        wind_penalty  = max(0, (3.0 - req.wspm) / 3.0) * 20.0
        humid_penalty = max(0, (req.dewp + 5) / 30.0) * 10.0
        rain_relief   = min(req.rain * 8.0, 15.0)

        # Region-aware base: let the ML model drive the base
        # raw_prediction itself IS the model's estimate — use it as the anchor
        # but scale it to India's real range
        # Kerala clean day: raw~15-25 → base~15-25
        # Delhi bad day:    raw~80-150 → base~70-130
        model_base = max(5.0, raw_prediction * 0.85)  # trust model, slight downscale for bias

        meteo_adjustment = wind_penalty + humid_penalty - rain_relief

        base_bg = model_base + meteo_adjustment

        # Spatial impacts
        t_impact = 40.0 * math.exp(-spatial['dist_traffic']    / 150.0) if spatial['dist_traffic']    < 1000 else 0
        i_impact = 30.0 * math.exp(-spatial['dist_industrial'] / 300.0) if spatial['dist_industrial'] < 1500 else 0
        f_bonus  =  8.0 * math.exp(-spatial['dist_forest']     / 200.0) if spatial['dist_forest']     <  800 else 0

        final_pm25 = base_bg + t_impact + i_impact - f_bonus
        final_pm25 = max(3.0, round(final_pm25, 2))

        # India NAQI breakpoints
        if final_pm25 < 30:    status = "Good"
        elif final_pm25 < 60:  status = "Satisfactory"
        elif final_pm25 < 90:  status = "Moderate"
        elif final_pm25 < 120: status = "Poor"
        elif final_pm25 < 250: status = "Very Poor"
        else:                  status = "Severe"

        insights = []
        if using_fallback:
            insights.append({
                "feature": "⚠ Estimated Spatial Data", "impact": "High",
                "desc": "India OSM shapefiles not loaded. Distances are weather-estimated. Download India shapefiles from Geofabrik for accurate GIS readings."
            })
        if t_impact > 1.5:
            insights.append({
                "feature": "Major Road Proximity", "impact": "High",
                "desc": f"The pinpoint is {int(spatial['dist_traffic'])}m from major infrastructure. Local exhaust affects this coordinate."
            })
        if i_impact > 1.5:
            insights.append({
                "feature": "Industrial Zone Proximity", "impact": "High",
                "desc": f"Industrial area detected {int(spatial['dist_industrial'])}m away. Particulate emissions elevate local PM2.5."
            })
        if f_bonus > 1.2:
            insights.append({
                "feature": "Natural Filtration", "impact": "Low",
                "desc": f"Nearby vegetative canopies ({int(spatial['dist_forest'])}m) act as a biological filter."
            })
        if wind_penalty > 10:
            insights.append({
                "feature": "Poor Atmospheric Dispersal", "impact": "High",
                "desc": f"Low wind speed ({req.wspm} m/s) is trapping local emissions, elevating PM2.5."
            })
        if req.wspm > 4.5:
            insights.append({
                "feature": "Atmospheric Dispersal", "impact": "Low",
                "desc": "Active air currents are efficiently dispersing local emissions."
            })
        if rain_relief > 5:
            insights.append({
                "feature": "Wet Deposition", "impact": "Low",
                "desc": f"Active rainfall ({req.rain} mm/h) is washing particulates from the atmosphere."
            })

        return {
            "pm25": final_pm25,
            "status": status,
            "fallback_mode": using_fallback,
            "report": {
                "dist_road":       round(spatial['dist_traffic'], 1),
                "dist_industrial": round(spatial['dist_industrial'], 1),
                "dist_forest":     round(spatial['dist_forest'], 1)
            },
            "insights": insights
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)