🌍 Belgium Air Pinpoint

Belgium Air Pinpoint is an end-to-end predictive intelligence system designed to bridge the "Resolution Gap" in urban air quality monitoring. While traditional monitoring stations are geographically sparse, this system provides street-level PM2.5 forecasting by fusing Gradient Boosting Machine Learning with high-resolution National GIS data.

🚀 Key Features

📍 Hyper-Local Precision: Predicts PM2.5 concentrations at specific coordinates using national road, industrial, and natural forest GIS layers.

🧠 Explainable AI (XAI): Uses surrogate SHAP logic to explain why a location is high-risk (e.g., "Low wind dispersal + High traffic proximity").

🔥 Dynamic Spatial Heatmaps: Visualizes continuous pollution clouds over neighborhoods using procedural dispersion modeling via Leaflet.heat.

⚡ High-Speed Spatial Indexing: Utilizes R-tree SINDEX logic to query infrastructure within a 200km radius in sub-second time.

🔍 Intelligent Search: Integrated geocoding search limited to the Belgian national boundary via the Nominatim API.

📏 Visual Ruler: Interactive UI element connecting user coordinates to the nearest primary pollution source.

📊 Model Performance

The core inference engine is an XGBoost Regressor trained on a massive multi-station dataset of 420,768 records.

Metric

Value

Coefficient of Determination ($R^2$)

0.9579

Mean Absolute Error (MAE)

9.8424 $\mu g/m^3$

Root Mean Square Error (RMSE)

22.5372 $\mu g/m^3$

[!TIP]
For a technical deep dive into the feature engineering and mathematical modeling, refer to the full research paper documentation included in this repository.

📦 Getting Started

📋 Prerequisites

Python 3.9+

Node.js v16+ & npm

OpenWeatherMap API Key (Obtainable at openweathermap.org)

🛠️ Installation & Setup

Clone the Repository

git clone [https://github.com/yourusername/belgium-air-pinpoint.git](https://github.com/yourusername/belgium-air-pinpoint.git)
cd belgium-air-pinpoint


Backend Configuration

cd backend
python -m venv .venv

# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt


Note: Ensure your spatial_data/ folder contains the required .shp files.

Frontend Configuration

cd ../frontend
npm install


🛠️ Usage

Running the System

Start Backend:

# Inside the backend directory
uvicorn main:app --reload


Start Frontend:

# Inside the frontend directory
npm start


Access Dashboard:

Open http://localhost:3000

Search for a city (e.g., "Antwerp") or click anywhere on the Belgian map.

🏗️ System Architecture

The project implements a decoupled 3-tier architecture:

Presentation Layer: React.js SPA utilizing Leaflet for geospatial rendering and procedural heatmap generation.

Logic Layer: FastAPI handling asynchronous meteorological fetching and SINDEX proximity querying.

Data Layer: Pre-trained XGBoost model with serialized feature pipelines for real-time inference.

👥 Research Group (KP290)

School of Computer Science and Engineering

Lovely Professional University

Supervisor: Mr. Manish Singh

📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

🙏 Acknowledgments

OpenStreetMap: National GIS infrastructure data.

OpenWeatherMap: Real-time atmospheric API.

IRCEL-CELINE: Air quality benchmarking standards in Belgium.
