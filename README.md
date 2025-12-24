# 🇸🇬 Singapore Live Transport Intelligence Dashboard

## 📌 Overview

Urban commuters face uncertainty due to traffic congestion and fluctuating public transport arrival times.
This project builds a **real-time transport analytics dashboard** using **Singapore government open APIs** to monitor live bus arrivals and traffic conditions, while applying **data science techniques** to detect delays, peak hours, and anomalies.

The dashboard refreshes automatically and presents insights through **interactive charts and maps**.

---

## 🎯 Objectives

* Visualize **real-time public transport data** in Singapore
* Analyze **traffic congestion patterns**
* Detect **peak hours and abnormal slowdowns**
* Demonstrate **end-to-end data science workflow**:

  * Data ingestion
  * Processing
  * Analytics
  * Visualization

---

## 📊 Features

### 🔴 Live Monitoring

* Real-time bus arrival timings
* Traffic speed indicators
* Auto-refresh every 30–60 seconds

### 🌍 Geospatial Visualization

* Interactive map of Singapore
* Congestion levels highlighted by color
* Bus stop and road segment overlays

### 🧠 Data Science & Analytics

* **Delay Analysis**
  Compare current traffic speed with historical averages
* **Peak Hour Detection**
  Identify congestion patterns by time of day
* **Anomaly Detection**
  Flag unexpected slowdowns in traffic conditions

### 📈 Insights Panel

Automatically generated insights such as:

* “Traffic speed is 38% below average at 8:45 AM”
* “Abnormal congestion detected on selected road segments”

---

## 🗂️ Data Sources

* **LTA DataMall (Singapore)**

  * Bus Arrival Timings
  * Traffic Speed Bands
* **OneMap API**

  * Geospatial data and mapping

All data sources are **official Singapore government open data APIs**.

---

## 🏗️ System Architecture

```
LTA DataMall APIs
        ↓
  Data Ingestion (Python)
        ↓
 Data Processing (Pandas)
        ↓
 Analytics Layer (Statistics / ML)
        ↓
 Streamlit Dashboard
```

---

## 🛠 Tech Stack

| Category         | Tools                |
| ---------------- | -------------------- |
| Language         | Python               |
| Data Processing  | Pandas               |
| Visualization    | Plotly               |
| Mapping          | PyDeck / Folium      |
| Dashboard        | Streamlit            |
| Machine Learning | Scikit-learn         |
| APIs             | LTA DataMall, OneMap |

---

## 📁 Project Structure

```
singapore-transport-dashboard/
│
├── data/
│   └── historical_data.csv
├── src/
│   ├── fetch_data.py
│   ├── process_data.py
│   ├── analytics.py
│   └── visualization.py
├── app.py
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Option 1: React Dashboard (Recommended)

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/azniosman/singapore-transport-intelligence.git
cd singapore-transport-intelligence
```

#### 2️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 3️⃣ Set API Keys

The `.env` file already contains your LTA DataMall API key.

#### 4️⃣ Start Backend API Server

```bash
python api_server.py
```

The API will start on `http://localhost:5000` with endpoints:
- `GET /api/bus_stops` - Returns all bus stops
- `GET /api/bus_arrivals` - Returns real-time bus arrivals
- `GET /api/health` - Health check

#### 5️⃣ Install Frontend Dependencies

In a new terminal:

```bash
npm install
```

#### 6️⃣ Start React Frontend

```bash
npm start
```

The dashboard will open at `http://localhost:3000`

### Option 2: Streamlit Dashboard (Original)

```bash
streamlit run main.py
```

---

## 📸 Screenshots

*(Add dashboard screenshots or a short GIF here)*

---

## 🔍 Key Learnings

* Working with **real-time government APIs**
* Handling **rate limits and polling strategies**
* Applying **data science techniques** to live data
* Building **interactive dashboards** for decision-making

---

## 🚧 Future Improvements

* Predictive delay modeling
* Historical trend comparison dashboard
* Alert notifications for severe congestion
* Cloud deployment with scheduled data storage

---

## 👤 Md. Azni Osman

**Your Name**
Data Science / Analytics Enthusiast
📫 LinkedIn | GitHub

___
