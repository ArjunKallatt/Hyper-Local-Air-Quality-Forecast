# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"India Air Pinpoint" — a full-stack app that predicts hyper-local PM2.5 air quality at a clicked map coordinate. It combines an XGBoost regression model with GIS proximity features (distance to major roads, industrial zones, forests) and live weather data. The model is trained on Beijing station data (2013–2017) but the deployed app is scoped to India (map bounds, UI copy, spatial data source).

## Architecture

The system has three parts that don't share code and must be run/updated independently:

1. **Training pipeline** (`scripts/`, `backend/merger.py`) — offline, run manually to (re)produce the model artifacts.
2. **Backend API** (`backend/main.py`) — FastAPI service that loads the trained model + GIS shapefiles at startup and serves `/predict`.
3. **Frontend** (`frontend/`) — single-page React app (Leaflet map + sidebar) that calls the backend and OpenWeatherMap directly from the browser.

### Training pipeline

- Raw data: `data/datasets/PRSA_Data_*.csv` — 12 Beijing monitoring stations, 2013–2017 (the Beijing Multi-Site Air Quality dataset).
- `backend/merger.py` concatenates the per-station CSVs, interpolates missing values, and adds cyclical hour/month features (`hour_sin/cos`, `month_sin/cos`).
- `scripts/add_spatial_features.py` and `scripts/train_model.py` both inject **simulated** spatial features (`dist_traffic`, `dist_industrial`, `dist_forest`, etc.) per station, since real India shapefiles aren't used at training time — the model learns the *relationship* between proximity and PM2.5 from synthetic per-station profiles, not from ground-truth India geodata. Only a couple of stations have explicit profiles in `STATION_FEATURES`/`spatial_profiles`; every other station falls back to a default/`Aotizhongxin` profile — extend these dicts if you add per-station realism.
- `scripts/train_model.py` currently hardcodes an absolute local dataset path (`/home/aaru/projects/...`) in `load_data()` — update this glob path before running it in any other environment.
- Training outputs `air_quality_model.pkl` and `model_features.pkl` into the current working directory; the backend expects them in `backend/`, so run training from `backend/` or move the artifacts there afterward.
- Model/feature `.pkl` files and `spatial_data/` (OSM shapefiles) are gitignored and **not present in the repo** — the backend will fail to load them on a fresh checkout until you train the model and download India OSM extracts (e.g. from Geofabrik) into `backend/spatial_data/`. `main.py` degrades gracefully (see fallback mode below) if either is missing, but predictions will be a weather-only heuristic, not GIS-grounded.

### Backend (`backend/main.py`)

- FastAPI app, single `POST /predict` endpoint. Loads the model and three GIS layers (roads filtered to motorway/trunk/primary, landuse filtered to industrial, natural filtered to forest/park/wood) once at import time using geopandas spatial indexes for fast nearest-distance queries.
- `/predict` blends the raw XGBoost output with hand-tuned heuristics: a meteorological adjustment (wind/humidity penalty, rain relief) and exponential-decay spatial impacts for traffic/industrial proximity and a forest "bonus". These constants (decay rates, weights, breakpoints) live inline in `main.py` — treat them as the actual scoring logic, not just presentation.
- **Fallback mode**: if the shapefiles are empty/missing (`using_fallback`), spatial distances are synthesized from atmospheric pressure instead of real GIS data, and the response's `insights` flags this so the frontend can warn the user. Don't assume `/predict` always reflects real geodata — check `fallback_mode` in the response.
- Final PM2.5 is bucketed into India NAQI categories (Good/Satisfactory/Moderate/Poor/Very Poor/Severe) with fixed breakpoints.
- Runs on `127.0.0.1:8000` (the frontend has this hardcoded — see below). Note the root `README.md` says port 5000; that's stale, `main.py` is the source of truth (8000).
- `backend/package.json` (axios/leaflet/react-leaflet) appears to be leftover cruft in a Python backend directory — not used by `main.py`; ignore it unless you're intentionally cleaning it up.

### Frontend (`frontend/src/App.js`)

- Everything lives in one component file with inline styles — no component decomposition, no CSS modules/framework.
- Leaflet is loaded dynamically via a CDN `<script>`/`<link>` tag at runtime (`window.L`) rather than through the `react-leaflet`/`leaflet` npm packages that are listed as dependencies — those packages are currently unused dead weight unless you migrate the map to use them properly.
- Calls two third-party APIs directly from the browser: OpenWeatherMap (for live temp/pressure/wind/rain at the clicked point — API key is hardcoded in `App.js`) and Nominatim (for place search, scoped to India via `countrycodes=in`).
- Calls the backend at hardcoded `http://127.0.0.1:8000/predict` — update this if deploying anywhere other than local dev.
- Map is bounded to India (`INDIA_BOUNDS`), default center is India's centroid.

## Commands

Backend:
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r ../requirements.txt   # requirements.txt lives at repo root, not in backend/
python main.py                        # serves on http://127.0.0.1:8000
```

Frontend:
```bash
cd frontend
npm install
npm start                             # serves on http://localhost:3000
```

Retrain the model (from `backend/`, after fixing the hardcoded path in `scripts/train_model.py`):
```bash
python ../scripts/train_model.py
```

There is no configured lint, CI, or backend test suite. The frontend only has the default Create React App test scaffold (`frontend/src/App.test.js`); run it with `npm test` inside `frontend/`.

## Notes

- `folders.txt` at the repo root is a stale local directory dump (includes `spatial_data/`, `.pkl` files, a notebook — none of which are actually tracked in git); don't treat it as the current file tree, use it only as a hint about what a fully set-up local dev environment looks like.
- The project's git history shows a pivot from a Belgium-focused prototype to an India-focused one (`data/processed/belgium_master_training_set.csv` is a remnant of the earlier iteration); expect occasional inconsistencies between naming/comments and the current India scope.
