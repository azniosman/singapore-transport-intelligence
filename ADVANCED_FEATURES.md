# Advanced Features Guide

This guide explains how to use the advanced predictive and analytics features of the Singapore Transport Intelligence Dashboard.

## 🎯 Overview of New Features

### 1. **Predictive Delay Modeling**
- Uses machine learning to predict bus arrival delays
- Based on historical patterns, time of day, and current load status
- Provides confidence scores for predictions

### 2. **Historical Trend Comparison**
- Compares current traffic conditions with historical averages
- Identifies peak hours and congestion patterns
- Generates automated insights

### 3. **Alert Notifications for Severe Congestion**
- Real-time monitoring and alert generation
- In-app notifications (displayed in dashboard)
- Email notifications (optional, configurable)
- Automatic alert resolution

---

## 📊 Getting Started

### Step 1: Collect Historical Data

Before using predictive features, you need to collect baseline data:

```bash
# Run data collector to start building historical database
python3 data_collector.py --once
```

Or run continuously (collects every 5 minutes):

```bash
python3 data_collector.py
```

**Recommended:** Run the collector for at least 24-48 hours to gather sufficient training data.

### Step 2: Train the ML Model

Once you have at least 100 data points:

```bash
# Train the predictive model
python3 predictive_model.py
```

Or use the API endpoint:

```bash
curl -X POST http://localhost:5000/api/train_model
```

### Step 3: Start the API Server

```bash
python3 api_server.py
```

The server will now serve predictions, trends, and alerts!

---

## 🚀 Using the Features

### Predictive Delay Modeling

**API Endpoint:** `GET /api/predictions`

Returns delay predictions for current bus arrivals.

**Example Response:**
```json
[
  {
    "BusStop": "01012",
    "BusNo": "7",
    "NextBusArrival": "2024-01-15T10:35:00+08:00",
    "Load": "SEA",
    "predicted_delay": 3.5,
    "confidence": 0.85
  }
]
```

**Fields:**
- `predicted_delay`: Predicted delay in minutes (positive = late, negative = early)
- `confidence`: Prediction confidence (0-1, higher is better)

**How It Works:**
- Analyzes 30 days of historical data
- Considers: hour of day, day of week, bus route, load status
- Uses Gradient Boosting ML algorithm
- Retrains automatically as more data is collected

---

### Historical Trend Comparison

**API Endpoint:** `GET /api/trends`

Returns comprehensive trend analysis.

**Example Response:**
```json
{
  "hourly_trends": [...],
  "current_vs_historical": {
    "current_hour": "2024-01-15T10:00:00",
    "current_stats": {
      "total_buses": 45,
      "avg_delay": 5.2,
      "severe_delays": 3
    },
    "historical_average": {
      "avg_delay": 3.8,
      "lsd_ratio": 0.15
    },
    "comparison": {
      "delay_change_percent": 36.8,
      "is_worse_than_usual": true,
      "congestion_level": "HIGH"
    }
  },
  "peak_hours": {
    "peak_hours": [8, 18, 17, 9, 19],
    "morning_peak_stats": {...},
    "evening_peak_stats": {...}
  },
  "insights": [
    "⚠️ Traffic delays are 37% higher than usual",
    "📊 Worst congestion typically occurs around 18:00"
  ]
}
```

**Congestion Levels:**
- `LOW`: Normal conditions
- `MODERATE`: Slightly elevated delays
- `HIGH`: Significant congestion
- `SEVERE`: Critical congestion levels

---

### Alert Notifications

**Get Active Alerts:** `GET /api/alerts`

Returns currently active alerts.

**Check for New Alerts:** `POST /api/alerts/check`

Manually trigger alert checking.

**Example Alert:**
```json
{
  "id": 1,
  "alert_type": "SEVERE_CONGESTION",
  "severity": "CRITICAL",
  "message": "Severe congestion detected across the network",
  "created_at": "2024-01-15T18:05:00",
  "details": {
    "avg_delay": 12.5,
    "severe_delays": 15,
    "lsd_count": 25
  }
}
```

**Alert Types:**
- `SEVERE_CONGESTION`: Network-wide severe congestion
- `UNUSUAL_DELAY`: Delays significantly higher than historical average
- `HIGH_LSD_RATIO`: Large number of crowded buses
- `SYSTEM_ANOMALY`: Unexpected system behavior

**Severity Levels:**
- `INFO`: Informational only
- `WARNING`: Attention recommended
- `CRITICAL`: Immediate attention required

---

## 📧 Email Notifications Setup

To receive email alerts, configure SMTP settings in `.env`:

```bash
# Gmail Example (use App Password, not regular password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your_app_password_here
ALERT_EMAIL_TO=recipient@example.com
```

**Gmail App Password Setup:**
1. Enable 2-Factor Authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a new app password for "Mail"
4. Use that 16-character password in `.env`

**Testing Email Alerts:**
```bash
python3 alerts.py
```

---

## 🗄️ Database Management

The system uses SQLite for data storage: `transport_intelligence.db`

**Tables:**
- `bus_arrivals`: Historical bus arrival records
- `delay_predictions`: ML prediction history
- `congestion_alerts`: Alert log
- `hourly_statistics`: Aggregated hourly stats

**Viewing Data:**
```bash
sqlite3 transport_intelligence.db

# Example queries:
sqlite> SELECT COUNT(*) FROM bus_arrivals;
sqlite> SELECT * FROM congestion_alerts ORDER BY created_at DESC LIMIT 5;
sqlite> .exit
```

**Backup Database:**
```bash
cp transport_intelligence.db transport_intelligence_backup.db
```

---

## ⚙️ Automated Operations

### Continuous Data Collection

Run data collector as a background service:

```bash
# Linux/Mac: Use nohup
nohup python3 data_collector.py > collector.log 2>&1 &

# Or use screen
screen -S collector
python3 data_collector.py
# Press Ctrl+A, then D to detach
```

### Periodic Model Retraining

Retrain model weekly to improve accuracy:

```bash
# Add to crontab
0 2 * * 0 cd /path/to/project && python3 predictive_model.py
```

### Alert Monitoring

The alert system runs automatically when you call `/api/alerts/check`.

Set up periodic checking (every 5 minutes):

```bash
# Crontab entry
*/5 * * * * curl -X POST http://localhost:5000/api/alerts/check
```

---

## 📈 Performance Tips

1. **Data Collection Interval**
   - Default: 5 minutes (300 seconds)
   - For testing: Use 60 seconds
   - For production: 300-600 seconds recommended

2. **Model Training Frequency**
   - Initial training: After 100+ records
   - Retraining: Weekly or when accuracy drops
   - Automatic retraining: Not implemented (manual only)

3. **Database Optimization**
   - Indexes are created automatically
   - Cleanup old data periodically:
     ```sql
     DELETE FROM bus_arrivals WHERE recorded_at < datetime('now', '-90 days');
     ```

4. **API Performance**
   - `/api/predictions`: ~500ms (with 100 arrivals)
   - `/api/trends`: ~200ms (with 7 days data)
   - `/api/alerts`: ~50ms

---

## 🔍 Troubleshooting

### "Model not trained yet"
**Problem:** `/api/predictions` returns 503 error

**Solution:**
```bash
# Check if you have enough data
python3 -c "from database import get_database; db = get_database(); print(len(db.get_historical_arrivals(days=30)))"

# If count >= 100, train the model
python3 predictive_model.py
```

### "No historical data available"
**Problem:** `/api/trends` returns empty results

**Solution:**
```bash
# Run data collector to gather data
python3 data_collector.py --once

# Wait and run again (needs multiple hours of data)
```

### Email alerts not sending
**Problem:** Alerts created but no emails received

**Solution:**
1. Check SMTP credentials in `.env`
2. Test SMTP connection:
   ```bash
   python3 alerts.py
   ```
3. Check spam folder
4. Verify Gmail App Password (not regular password)

### Database locked errors
**Problem:** `database is locked` error

**Solution:**
- Only run one data collector instance
- Close any open database connections
- Restart API server

---

## 📝 Example Workflow

### Complete Setup from Scratch

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Download bus stops data
python3 download_bus_stops.py

# 3. Start collecting data (run for 24 hours)
python3 data_collector.py

# After 24 hours...

# 4. Train the model
python3 predictive_model.py

# 5. Start API server
python3 api_server.py

# 6. In another terminal, start frontend
npm start

# 7. Access dashboard at http://localhost:3000
```

### Daily Operations

```bash
# Morning: Check alerts
curl http://localhost:5000/api/alerts

# Monitor trends
curl http://localhost:5000/api/trends | python3 -m json.tool

# Force alert check
curl -X POST http://localhost:5000/api/alerts/check
```

---

## 🎓 Understanding the ML Model

**Algorithm:** Gradient Boosting Regressor

**Features Used:**
- Hour of day (0-23)
- Day of week (0-6)
- Is weekend (0/1)
- Is peak hour (0/1)
- Bus stop code (encoded)
- Bus service number (encoded)
- Current load status (SEA/SDA/LSD)

**Training Metrics:**
- R² Score: Measures prediction accuracy (higher is better)
- MAE (Mean Absolute Error): Average prediction error in minutes
- RMSE: Root mean squared error

**Example Output:**
```
Training Results:
  training_records: 5234
  valid_records: 5234
  train_r2_score: 0.782
  test_r2_score: 0.745
  mean_absolute_error: 2.34 minutes
  rmse: 3.12 minutes
```

---

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review `API_TESTING.md` for API usage
3. Check logs in `collector.log`
4. Review database contents with sqlite3

---

*Last Updated: December 2024*
