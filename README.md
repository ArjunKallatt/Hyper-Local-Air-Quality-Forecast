🌍 Belgium Air Pinpoint

Belgium Air Pinpoint is an end-to-end predictive intelligence system designed to bridge the "Resolution Gap" in urban air quality monitoring. While traditional monitoring stations are sparse, this system provides street-level PM2.5 forecasting by fusing Gradient Boosting Machine Learning with high-resolution National GIS data.

🚀 Features

Hyper-Local Precision: Predicts PM2.5 concentrations at specific coordinates using national road, industrial, and natural forest GIS layers.

Explainable AI (XAI): Uses surrogate SHAP logic to explain why a location is high-risk (e.g., "Low wind dispersal + High traffic proximity").

Dynamic Spatial Heatmaps: Visualizes continuous pollution clouds over neighborhoods using procedural dispersion modeling via Leaflet.heat.

High-Speed Spatial Indexing: Utilizes R-tree SINDEX logic to query infrastructure within a 200km radius in sub-second time.

Intelligent Search: Integrated geocoding search limited to the Belgian national boundary via the Nominatim API.

Visual Ruler: Interactive UI element connecting user coordinates to the nearest primary pollution source.

📊 Model Performance

The core inference engine is an XGBoost Regressor trained on 420,768 records.

Metric

Value

Coefficient of Determination ($R^2$)

0.9579

Mean Absolute Error (MAE)

9.8424 $\mu g/m^3$

Root Mean Square Error (RMSE)

22.5372 $\mu g/m^3$

For a deep dive into the math, see the Model Logic Breakdown.

📦 Getting Started

Prerequisites

Python 3.9+

Node.js v16+ & npm

OpenWeatherMap API Key (Get one at openweathermap.org)

Installation

1. Clone the Repository

git clone [https://github.com/yourusername/belgium-air-pinpoint.git](https://github.com/yourusername/belgium-air-pinpoint.git)
cd belgium-air-pinpoint


2. Backend Setup

cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt


Note: Ensure your spatial_data/ directory contains the required .shp files.

3. Frontend Setup

cd ../frontend
npm install


🛠️ Usage

Running the Application

Start the Backend Server:

# From the backend directory
uvicorn main:app --reload


Start the Frontend Dashboard:

# From the frontend directory
npm start


Analyze Air Quality:

Open http://localhost:3000 in your browser.

Click anywhere on the map of Belgium to trigger a hyper-local report.

Use the search bar to find specific municipalities.

API Documentation

Once the backend is running, visit http://127.0.0.1:8000/docs for the interactive Swagger UI.

🏗️ System Architecture

The project follows a decoupled 3-tier architecture:

Presentation Layer: React SPA using Leaflet for geospatial rendering.

Logic Layer: FastAPI handling asynchronous requests and feature engineering.

Data/ML Layer: XGBoost model and GeoPandas spatial indexing.

For more details, refer to the Technology Stack Overview.

🤝 Contributing

Contributions are welcome! Please follow these steps:

Fork the Project.

Create your Feature Branch (git checkout -b feature/AmazingFeature).

Commit your Changes (git commit -m 'Add some AmazingFeature').

Push to the Branch (git push origin feature/AmazingFeature).

Open a Pull Request.

Please read our CONTRIBUTING.md for details on our code of conduct.

📜 License

Distributed under the MIT License. See LICENSE for more information.

🙏 Acknowledgments

OpenStreetMap: For foundational national GIS shapefiles.

OpenWeatherMap: For real-time atmospheric data.

IRCEL-CELINE: For air quality benchmarking data in Belgium.

Lucide Icons: For clean, professional UI iconography.

👥 Research Group (KP290)

School of Computer Science and Engineering, Lovely Professional University

Supervisor: Mr. Manish Singh
