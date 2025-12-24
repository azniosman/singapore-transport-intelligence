import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

/**
 * Component to automatically adjust map bounds to show all markers
 */
const MapBoundsUpdater = ({ busStops }) => {
  const map = useMap();

  useEffect(() => {
    if (busStops && busStops.length > 0) {
      // Create bounds from all bus stop coordinates
      const bounds = busStops.map(stop => [stop.Latitude, stop.Longitude]);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [busStops, map]);

  return null;
};

/**
 * Get color based on bus load level
 * SEA (Seats Available) = Green
 * SDA (Standing Available) = Yellow
 * LSD (Limited Standing) = Red
 */
const getLoadColor = (load) => {
  switch (load) {
    case 'SEA':
      return '#22c55e'; // Green
    case 'SDA':
      return '#eab308'; // Yellow
    case 'LSD':
      return '#ef4444'; // Red
    default:
      return '#94a3b8'; // Gray (no data)
  }
};

/**
 * Format arrival time to display minutes remaining
 */
const formatArrivalTime = (isoString) => {
  if (!isoString) return 'N/A';

  const arrivalTime = new Date(isoString);
  const now = new Date();
  const diffMinutes = Math.round((arrivalTime - now) / 60000);

  if (diffMinutes < 0) return 'Arrived';
  if (diffMinutes === 0) return 'Arriving';
  return `${diffMinutes} min`;
};

/**
 * Map Component
 * Displays bus stops on an interactive Leaflet map with color-coded markers
 * based on bus load levels
 */
const Map = ({ busStops, busArrivals, selectedBusNumber }) => {
  // Merge bus stops with their arrival data
  const busStopsWithArrivals = useMemo(() => {
    if (!busStops || !busArrivals) return [];

    return busStops.map(stop => {
      // Find all arrivals for this bus stop
      let arrivals = busArrivals.filter(
        arrival => arrival.BusStop === stop.BusStopCode
      );

      // Filter by selected bus number if specified
      if (selectedBusNumber) {
        arrivals = arrivals.filter(
          arrival => arrival.BusNo === selectedBusNumber
        );
      }

      // Determine the most critical load level (LSD > SDA > SEA)
      let overallLoad = 'N/A';
      if (arrivals.length > 0) {
        if (arrivals.some(a => a.Load === 'LSD')) overallLoad = 'LSD';
        else if (arrivals.some(a => a.Load === 'SDA')) overallLoad = 'SDA';
        else if (arrivals.some(a => a.Load === 'SEA')) overallLoad = 'SEA';
      }

      return {
        ...stop,
        arrivals,
        overallLoad
      };
    });
  }, [busStops, busArrivals, selectedBusNumber]);

  // Filter out bus stops with no arrivals if a bus number is selected
  const displayedBusStops = selectedBusNumber
    ? busStopsWithArrivals.filter(stop => stop.arrivals.length > 0)
    : busStopsWithArrivals;

  // Default center: Singapore
  const defaultCenter = [1.3521, 103.8198];

  return (
    <MapContainer
      center={defaultCenter}
      zoom={12}
      style={{ height: '100%', width: '100%' }}
      className="bus-map"
    >
      {/* OpenStreetMap tiles */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Update map bounds when bus stops change */}
      {displayedBusStops.length > 0 && (
        <MapBoundsUpdater busStops={displayedBusStops} />
      )}

      {/* Render bus stop markers */}
      {displayedBusStops.map(stop => (
        <CircleMarker
          key={stop.BusStopCode}
          center={[stop.Latitude, stop.Longitude]}
          radius={8}
          fillColor={getLoadColor(stop.overallLoad)}
          color="#fff"
          weight={2}
          opacity={1}
          fillOpacity={0.8}
        >
          {/* Tooltip popup on click */}
          <Popup>
            <div className="bus-stop-popup">
              <h3>{stop.Description}</h3>
              <p className="bus-stop-code">
                <strong>Stop Code:</strong> {stop.BusStopCode}
              </p>

              {stop.arrivals.length > 0 ? (
                <div className="arrivals-list">
                  <h4>Next Arrivals:</h4>
                  {stop.arrivals.map((arrival, idx) => (
                    <div key={idx} className="arrival-item">
                      <span className="bus-number">Bus {arrival.BusNo}</span>
                      <span className="arrival-time">
                        {formatArrivalTime(arrival.NextBusArrival)}
                      </span>
                      <span
                        className="load-indicator"
                        style={{
                          backgroundColor: getLoadColor(arrival.Load),
                          color: '#fff',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontSize: '0.75rem'
                        }}
                      >
                        {arrival.Load}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-arrivals">No arrivals available</p>
              )}
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
};

export default Map;
