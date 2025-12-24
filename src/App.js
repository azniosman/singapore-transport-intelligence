import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Map from './components/Map';
import Sidebar from './components/Sidebar';
import './App.css';

/**
 * Main App Component
 * Manages state, data fetching, and auto-refresh for the Singapore Transport Dashboard
 */
function App() {
  // State management
  const [busStops, setBusStops] = useState([]);
  const [busArrivals, setBusArrivals] = useState([]);
  const [selectedBusNumber, setSelectedBusNumber] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // API configuration
  // Update this URL to point to your backend API
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  /**
   * Fetch bus stops data from the API
   * This data is relatively static and only needs to be fetched once
   */
  const fetchBusStops = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/bus_stops`);
      setBusStops(response.data);
    } catch (err) {
      console.error('Error fetching bus stops:', err);
      setError('Failed to fetch bus stops. Using mock data.');

      // Mock data for development/testing
      setBusStops([
        {
          BusStopCode: '01012',
          Description: 'Victoria St',
          Latitude: 1.29684825487647,
          Longitude: 103.85253591654006
        },
        {
          BusStopCode: '01013',
          Description: 'Raffles Blvd',
          Latitude: 1.29770970610083,
          Longitude: 103.85794034558846
        },
        {
          BusStopCode: '01019',
          Description: 'Bras Basah Rd',
          Latitude: 1.29698951191332,
          Longitude: 103.85302201563841
        }
      ]);
    }
  }, [API_BASE_URL]);

  /**
   * Fetch bus arrivals data from the API
   * This data is real-time and needs to be refreshed periodically
   */
  const fetchBusArrivals = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/bus_arrivals`);
      setBusArrivals(response.data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      console.error('Error fetching bus arrivals:', err);
      setError('Failed to fetch bus arrivals. Using mock data.');

      // Mock data for development/testing
      const mockArrivals = [
        {
          BusStop: '01012',
          BusNo: '7',
          NextBusArrival: new Date(Date.now() + 5 * 60000).toISOString(),
          Load: 'SEA'
        },
        {
          BusStop: '01012',
          BusNo: '14',
          NextBusArrival: new Date(Date.now() + 3 * 60000).toISOString(),
          Load: 'SDA'
        },
        {
          BusStop: '01013',
          BusNo: '16',
          NextBusArrival: new Date(Date.now() + 7 * 60000).toISOString(),
          Load: 'LSD'
        },
        {
          BusStop: '01013',
          BusNo: '7',
          NextBusArrival: new Date(Date.now() + 10 * 60000).toISOString(),
          Load: 'SEA'
        },
        {
          BusStop: '01019',
          BusNo: '14',
          NextBusArrival: new Date(Date.now() + 2 * 60000).toISOString(),
          Load: 'SDA'
        }
      ];
      setBusArrivals(mockArrivals);
      setLastUpdated(new Date());
    } finally {
      setIsLoading(false);
    }
  }, [API_BASE_URL]);

  /**
   * Initial data fetch on component mount
   */
  useEffect(() => {
    fetchBusStops();
    fetchBusArrivals();
  }, [fetchBusStops, fetchBusArrivals]);

  /**
   * Set up auto-refresh interval for bus arrivals
   * Refreshes every 30 seconds
   */
  useEffect(() => {
    const REFRESH_INTERVAL = 30000; // 30 seconds
    const intervalId = setInterval(() => {
      fetchBusArrivals();
    }, REFRESH_INTERVAL);

    // Cleanup interval on component unmount
    return () => clearInterval(intervalId);
  }, [fetchBusArrivals]);

  return (
    <div className="app">
      {/* Error banner */}
      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      {/* Sidebar with filters and statistics */}
      <Sidebar
        busArrivals={busArrivals}
        selectedBusNumber={selectedBusNumber}
        setSelectedBusNumber={setSelectedBusNumber}
        lastUpdated={lastUpdated}
        isLoading={isLoading}
      />

      {/* Map view */}
      <div className="map-container">
        <Map
          busStops={busStops}
          busArrivals={busArrivals}
          selectedBusNumber={selectedBusNumber}
        />
      </div>
    </div>
  );
}

export default App;
