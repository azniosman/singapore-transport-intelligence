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

### 📈 Advanced Features ⭐ NEW

* **🤖 Predictive Delay Modeling**
  Machine learning model predicts bus arrival delays based on historical patterns

* **📊 Historical Trend Comparison**
  Compare current conditions with historical data to identify unusual patterns

* **🚨 Alert Notifications for Severe Congestion**
  Real-time monitoring with in-app and email notifications

* **💾 SQLite Database**
  Stores historical data for analysis and model training

### 📈 Insights Panel

Automatically generated insights such as:

* "Traffic speed is 38% below average at 8:45 AM"
* "Abnormal congestion detected on selected road segments"
* "⚠️ Traffic delays are 37% higher than usual"
* "📊 Worst congestion typically occurs around 18:00"

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

Or use pip3 if pip is not available:
```bash
pip3 install -r requirements.txt
```

#### 3️⃣ Set API Keys

The `.env` file contains your LTA DataMall API key. Verify it's set:
```bash
cat .env | grep LTA_API_KEY
```

#### 4️⃣ Download Bus Stops Data (Recommended)

For better performance, download the bus stops data once:
```bash
python3 download_bus_stops.py
```

This creates `bus_stops.csv` with ~5,000 bus stops, making the API faster.

#### 5️⃣ Start Backend API Server

```bash
python3 api_server.py
```

The API will start on `http://localhost:5000` with endpoints:
- `GET /api/bus_stops` - Returns all bus stops (~5,000 stops)
- `GET /api/bus_arrivals` - Returns real-time bus arrivals (100 stops)
- `GET /api/health` - Health check

#### 6️⃣ Install Frontend Dependencies

In a new terminal:

```bash
npm install
```

#### 7️⃣ Start React Frontend

```bash
npm start
```

The dashboard will open at `http://localhost:3000`

---

### 🌟 Advanced Features Setup (Optional)

To use predictive modeling, historical trends, and alerts:

#### 1️⃣ Start Data Collection

```bash
# Run once to test
python3 data_collector.py --once

# Or run continuously (collects every 5 minutes)
python3 data_collector.py
```

Run for at least 24 hours to gather training data.

#### 2️⃣ Train ML Model

```bash
# After collecting 100+ records
python3 predictive_model.py
```

#### 3️⃣ Configure Email Alerts (Optional)

Edit `.env` file:
```bash
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
ALERT_EMAIL_TO=recipient@example.com
```

**📖 Full Guide:** See `ADVANCED_FEATURES.md` for detailed instructions

---

### Option 2: Streamlit Dashboard (Original)

```bash
streamlit run main.py
```

---

## 📝 Recent Updates

### December 2024 - Major Feature Release 🎉
- ⭐ **NEW:** Predictive delay modeling using machine learning
- ⭐ **NEW:** Historical trend comparison and analytics
- ⭐ **NEW:** Alert notifications for severe congestion (in-app + email)
- ⭐ **NEW:** SQLite database for historical data storage
- ⭐ **NEW:** Data collector service for continuous monitoring
- ✅ Added 5 new API endpoints for advanced features
- ✅ Created comprehensive `ADVANCED_FEATURES.md` guide
- ✅ Fixed API endpoint URLs from HTTP to HTTPS
- ✅ Updated `download_bus_stops.py` to use LTA DataMall API directly
- ✅ Added comprehensive troubleshooting guide
- ✅ Improved setup instructions with virtual environment support
- ✅ Added API testing documentation (`API_TESTING.md`)

---

## ⚠️ Important Notes

### API Endpoints
All LTA DataMall API endpoints use **HTTPS**:
- ✅ `https://datamall2.mytransport.sg/ltaodataservice/BusStops`
- ✅ `https://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2`

**Note:** Using `http://` will result in 404 errors.

### Performance Considerations
- **Bus Stops API**: Fast (~100ms) after initial load, data is cached
- **Bus Arrivals API**: Slower (30-60 seconds) as it fetches from 100 bus stops in real-time
- **Recommended**: Run `download_bus_stops.py` first to create a local CSV cache

---

## 🔧 Troubleshooting

### Download Script Returns 404
**Problem:** `python3 download_bus_stops.py` fails with 404 error

**Solutions:**
1. Ensure you're using the latest code (uses HTTPS)
2. Verify API key is correct in `.env` file
3. Check your internet connection
4. Verify API key has access at [LTA DataMall](https://datamall.lta.gov.sg/)

### Module Not Found Errors
**Problem:** `ModuleNotFoundError: No module named 'flask'` or similar

**Solution:** Install dependencies:
```bash
pip3 install -r requirements.txt
```

If using system Python on macOS, you may need to use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### API Returns No Data
**Problem:** Endpoints return empty arrays

**Solutions:**
1. Check API key is valid and active
2. Verify you're connected to the internet
3. Check LTA API status (may have rate limits: 500 req/sec)
4. Try testing with curl:
   ```bash
   curl -H "AccountKey: YOUR_KEY" \
     "https://datamall2.mytransport.sg/ltaodataservice/BusStops?\$skip=0"
   ```

### Frontend Can't Connect to Backend
**Problem:** React app shows "Failed to fetch" errors

**Solutions:**
1. Ensure backend is running on `http://localhost:5000`
2. Check CORS is enabled (already configured in `api_server.py`)
3. Verify `.env` has `REACT_APP_API_URL=http://localhost:5000`

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

* ~~Predictive delay modeling~~ ✅ IMPLEMENTED
* ~~Historical trend comparison dashboard~~ ✅ IMPLEMENTED
* ~~Alert notifications for severe congestion~~ ✅ IMPLEMENTED
* Real-time WebSocket updates for live data streaming
* Mobile app version
* Integration with traffic camera feeds
* Cloud deployment with scheduled data storage
* Multi-city support (expandable to other countries)

---

## 👤 Md. Azni Osman

**Your Name**
Data Science / Analytics Enthusiast
📫 LinkedIn | GitHub

___
