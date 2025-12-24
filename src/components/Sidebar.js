import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

/**
 * Sidebar Component
 * Displays filters, statistics, and load distribution chart
 */
const Sidebar = ({
  busArrivals,
  selectedBusNumber,
  setSelectedBusNumber,
  lastUpdated,
  isLoading
}) => {
  // Calculate statistics from bus arrivals
  const statistics = useMemo(() => {
    if (!busArrivals || busArrivals.length === 0) {
      return {
        totalBuses: 0,
        uniqueRoutes: 0,
        loadDistribution: []
      };
    }

    // Count unique bus routes
    const uniqueRoutes = new Set(busArrivals.map(a => a.BusNo)).size;

    // Calculate load distribution
    const loadCounts = busArrivals.reduce((acc, arrival) => {
      acc[arrival.Load] = (acc[arrival.Load] || 0) + 1;
      return acc;
    }, {});

    const loadDistribution = [
      { name: 'Seats Available (SEA)', value: loadCounts.SEA || 0, color: '#22c55e' },
      { name: 'Standing Available (SDA)', value: loadCounts.SDA || 0, color: '#eab308' },
      { name: 'Limited Standing (LSD)', value: loadCounts.LSD || 0, color: '#ef4444' }
    ].filter(item => item.value > 0);

    return {
      totalBuses: busArrivals.length,
      uniqueRoutes,
      loadDistribution
    };
  }, [busArrivals]);

  // Get unique bus numbers for filter dropdown
  const uniqueBusNumbers = useMemo(() => {
    if (!busArrivals) return [];
    const numbers = [...new Set(busArrivals.map(a => a.BusNo))];
    return numbers.sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  }, [busArrivals]);

  /**
   * Format timestamp to readable time
   */
  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <h1>🇸🇬 Singapore Transport Intelligence</h1>
        <p className="subtitle">Real-time Bus Monitoring Dashboard</p>
      </div>

      {/* Status indicator */}
      <div className="status-section">
        <div className={`status-indicator ${isLoading ? 'loading' : 'active'}`}>
          <span className="status-dot"></span>
          <span>{isLoading ? 'Updating...' : 'Live'}</span>
        </div>
        <p className="last-updated">
          Last updated: {formatTime(lastUpdated)}
        </p>
      </div>

      {/* Filter Section */}
      <div className="filter-section">
        <h2>🔍 Filters</h2>
        <div className="filter-group">
          <label htmlFor="bus-number-filter">Bus Number:</label>
          <select
            id="bus-number-filter"
            value={selectedBusNumber}
            onChange={(e) => setSelectedBusNumber(e.target.value)}
            className="filter-select"
          >
            <option value="">All Buses</option>
            {uniqueBusNumbers.map(busNo => (
              <option key={busNo} value={busNo}>
                Bus {busNo}
              </option>
            ))}
          </select>
        </div>
        {selectedBusNumber && (
          <button
            onClick={() => setSelectedBusNumber('')}
            className="clear-filter-btn"
          >
            Clear Filter
          </button>
        )}
      </div>

      {/* Statistics Section */}
      <div className="statistics-section">
        <h2>📊 Statistics</h2>
        <div className="stat-cards">
          <div className="stat-card">
            <div className="stat-value">{statistics.totalBuses}</div>
            <div className="stat-label">Total Arrivals</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{statistics.uniqueRoutes}</div>
            <div className="stat-label">Active Routes</div>
          </div>
        </div>
      </div>

      {/* Load Distribution Chart */}
      {statistics.loadDistribution.length > 0 && (
        <div className="chart-section">
          <h2>📈 Load Distribution</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={statistics.loadDistribution}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label={(entry) => `${entry.value}`}
              >
                {statistics.loadDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Legend */}
      <div className="legend-section">
        <h3>Legend</h3>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#22c55e' }}></span>
            <span>SEA - Seats Available</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#eab308' }}></span>
            <span>SDA - Standing Available</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#ef4444' }}></span>
            <span>LSD - Limited Standing</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <p>Auto-refreshes every 30 seconds</p>
      </div>
    </div>
  );
};

export default Sidebar;
