# API Testing Guide

This document explains how to test the backend API endpoints.

## Prerequisites

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your `.env` file has the LTA API key:
```
LTA_API_KEY=your_api_key_here
```

## Download Bus Stops Data (Optional but Recommended)

For better performance, download the static bus stops CSV file:

```bash
python download_bus_stops.py
```

This creates a `bus_stops.csv` file that the API server will use instead of calling the LTA API every time.

## Start the API Server

```bash
python api_server.py
```

The server will start on `http://localhost:5000`

You should see:
```
============================================================
Singapore Transport Intelligence API Server
============================================================
API Key configured: True
Starting server on http://localhost:5000
============================================================
```

## Test Endpoints

### 1. Health Check

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000000",
  "api_key_configured": true
}
```

### 2. Get Bus Stops

```bash
curl http://localhost:5000/api/bus_stops
```

Expected response (truncated):
```json
[
  {
    "BusStopCode": "01012",
    "Description": "Hotel Grand Pacific",
    "Latitude": 1.29684825487647,
    "Longitude": 103.85253591654006
  },
  {
    "BusStopCode": "01013",
    "Description": "St. Joseph's Ch",
    "Latitude": 1.29770970610083,
    "Longitude": 103.85794034558846
  },
  ...
]
```

### 3. Get Bus Arrivals

**Note:** This endpoint fetches data for 100 bus stops and may take 30-60 seconds.

```bash
curl http://localhost:5000/api/bus_arrivals
```

Expected response (truncated):
```json
[
  {
    "BusStop": "01012",
    "BusNo": "7",
    "NextBusArrival": "2024-01-15T10:35:00+08:00",
    "Load": "SEA"
  },
  {
    "BusStop": "01012",
    "BusNo": "14",
    "NextBusArrival": "2024-01-15T10:33:00+08:00",
    "Load": "SDA"
  },
  ...
]
```

## Load Status Codes

- **SEA** - Seats Available (Green)
- **SDA** - Standing Available (Yellow)
- **LSD** - Limited Standing (Red)

## Performance Notes

- **Bus Stops**: Cached after first request, very fast (~100ms)
- **Bus Arrivals**: Fetches from 100 stops, takes 30-60 seconds
  - In production, consider:
    - Limiting to user's location/area
    - Caching with TTL
    - Background workers
    - WebSocket updates

## Testing with the React Frontend

1. Start the backend API (this server)
2. In another terminal, start the React app:
   ```bash
   npm start
   ```
3. Open `http://localhost:3000` in your browser
4. The map should display bus stops with real-time arrival data

## Common Issues

### API Key Not Working
- Check `.env` file has correct `LTA_API_KEY`
- Verify API key is active at [LTA DataMall](https://datamall.lta.gov.sg/)

### No Data Returned
- Check API key is valid
- Ensure internet connection is stable
- LTA API might be rate-limited (500 requests/sec limit)

### Slow Response
- Download `bus_stops.csv` using `download_bus_stops.py`
- Consider reducing number of stops in `api_server.py` line 149
