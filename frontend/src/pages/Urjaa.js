import React, { useState } from 'react';
import { 
  Zap, MapPin, Battery, TrendingUp, Users, 
  Activity, AlertCircle, CheckCircle, Clock 
} from 'lucide-react';
import './Urjaa.css';

const Urjaa = () => {
  const [selectedStation, setSelectedStation] = useState(null);

  // Mock data for URGAA EV Charging stations
  const stations = [
    {
      id: 'URG001',
      name: 'Go4Garage Hub - Sector 18',
      location: 'Noida, UP',
      status: 'operational',
      chargers: {
        total: 8,
        available: 5,
        occupied: 2,
        maintenance: 1
      },
      utilization: 72,
      revenue: 45320,
      sessions: 156,
      coordinates: { lat: 28.5672, lng: 77.3220 }
    },
    {
      id: 'URG002',
      name: 'URGAA Express - DLF Phase 3',
      location: 'Gurugram, HR',
      status: 'operational',
      chargers: {
        total: 12,
        available: 7,
        occupied: 4,
        maintenance: 1
      },
      utilization: 68,
      revenue: 67890,
      sessions: 234,
      coordinates: { lat: 28.4935, lng: 77.0932 }
    },
    {
      id: 'URG003',
      name: 'Green Energy Hub - Connaught Place',
      location: 'New Delhi, DL',
      status: 'operational',
      chargers: {
        total: 16,
        available: 3,
        occupied: 12,
        maintenance: 1
      },
      utilization: 87,
      revenue: 98450,
      sessions: 412,
      coordinates: { lat: 28.6315, lng: 77.2167 }
    },
    {
      id: 'URG004',
      name: 'URGAA Tech Park - Whitefield',
      location: 'Bangalore, KA',
      status: 'operational',
      chargers: {
        total: 20,
        available: 12,
        occupied: 6,
        maintenance: 2
      },
      utilization: 55,
      revenue: 54230,
      sessions: 178,
      coordinates: { lat: 12.9698, lng: 77.7499 }
    },
    {
      id: 'URG005',
      name: 'Smart Charge - Hitech City',
      location: 'Hyderabad, TG',
      status: 'maintenance',
      chargers: {
        total: 10,
        available: 0,
        occupied: 0,
        maintenance: 10
      },
      utilization: 0,
      revenue: 12450,
      sessions: 45,
      coordinates: { lat: 17.4485, lng: 78.3908 }
    },
    {
      id: 'URG006',
      name: 'URGAA Green Zone - Salt Lake',
      location: 'Kolkata, WB',
      status: 'operational',
      chargers: {
        total: 14,
        available: 8,
        occupied: 5,
        maintenance: 1
      },
      utilization: 62,
      revenue: 43210,
      sessions: 189,
      coordinates: { lat: 22.5726, lng: 88.3639 }
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'operational': return '#4CAF50';
      case 'maintenance': return '#FF9800';
      case 'offline': return '#F44336';
      default: return '#999';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'operational': return <CheckCircle size={16} />;
      case 'maintenance': return <Clock size={16} />;
      case 'offline': return <AlertCircle size={16} />;
      default: return null;
    }
  };

  const getUtilizationColor = (utilization) => {
    if (utilization >= 80) return '#4CAF50';
    if (utilization >= 50) return '#FF9800';
    return '#F44336';
  };

  // Calculate totals
  const totals = stations.reduce((acc, station) => ({
    stations: acc.stations + 1,
    totalChargers: acc.totalChargers + station.chargers.total,
    availableChargers: acc.availableChargers + station.chargers.available,
    revenue: acc.revenue + station.revenue,
    sessions: acc.sessions + station.sessions
  }), { stations: 0, totalChargers: 0, availableChargers: 0, revenue: 0, sessions: 0 });

  const avgUtilization = Math.round(
    stations.reduce((sum, s) => sum + s.utilization, 0) / stations.length
  );

  return (
    <div className="urjaa-container">
      {/* Header */}
      <div className="urjaa-header">
        <div className="header-left">
          <h1>
            <Zap size={32} className="urjaa-icon" />
            URJAA EV Charging Network
          </h1>
          <p className="urjaa-subtitle">
            Real-time charging station monitoring and management
          </p>
        </div>
        <div className="header-brand">
          <div className="brand-pill">
            <Zap size={16} />
            <span>Made in Bharat</span>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#0A3D62' }}>
            <MapPin size={24} />
          </div>
          <div className="stat-details">
            <p className="stat-label">Total Stations</p>
            <h2 className="stat-value">{totals.stations}</h2>
            <p className="stat-change positive">
              <TrendingUp size={14} />
              +2 this month
            </p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#4CAF50' }}>
            <Battery size={24} />
          </div>
          <div className="stat-details">
            <p className="stat-label">Available Chargers</p>
            <h2 className="stat-value">{totals.availableChargers}/{totals.totalChargers}</h2>
            <p className="stat-change neutral">
              {Math.round((totals.availableChargers / totals.totalChargers) * 100)}% available
            </p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#FFC312' }}>
            <Activity size={24} />
          </div>
          <div className="stat-details">
            <p className="stat-label">Avg. Utilization</p>
            <h2 className="stat-value">{avgUtilization}%</h2>
            <p className="stat-change positive">
              <TrendingUp size={14} />
              +8% from last month
            </p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#8e24aa' }}>
            <Users size={24} />
          </div>
          <div className="stat-details">
            <p className="stat-label">Total Sessions</p>
            <h2 className="stat-value">{totals.sessions.toLocaleString()}</h2>
            <p className="stat-change positive">
              <TrendingUp size={14} />
              +15% this week
            </p>
          </div>
        </div>
      </div>

      {/* Stations Grid */}
      <div className="stations-section">
        <div className="section-header">
          <h2>Charging Stations</h2>
          <p className="section-subtitle">Click a station to view details</p>
        </div>

        <div className="stations-grid">
          {stations.map(station => (
            <div 
              key={station.id}
              className={`station-card ${selectedStation?.id === station.id ? 'selected' : ''}`}
              onClick={() => setSelectedStation(station)}
            >
              <div className="station-header">
                <div className="station-title">
                  <h3>{station.name}</h3>
                  <p className="station-location">
                    <MapPin size={14} />
                    {station.location}
                  </p>
                </div>
                <div 
                  className="station-status"
                  style={{ 
                    background: getStatusColor(station.status) + '20',
                    color: getStatusColor(station.status)
                  }}
                >
                  {getStatusIcon(station.status)}
                  {station.status}
                </div>
              </div>

              <div className="station-stats">
                <div className="station-stat">
                  <span className="stat-icon-small">
                    <Battery size={16} />
                  </span>
                  <div>
                    <p className="stat-small-label">Chargers</p>
                    <p className="stat-small-value">
                      {station.chargers.available} / {station.chargers.total}
                    </p>
                  </div>
                </div>

                <div className="station-stat">
                  <span className="stat-icon-small">
                    <Activity size={16} />
                  </span>
                  <div>
                    <p className="stat-small-label">Utilization</p>
                    <p 
                      className="stat-small-value"
                      style={{ color: getUtilizationColor(station.utilization) }}
                    >
                      {station.utilization}%
                    </p>
                  </div>
                </div>
              </div>

              <div className="station-utilization-bar">
                <div 
                  className="utilization-fill"
                  style={{ 
                    width: `${station.utilization}%`,
                    background: getUtilizationColor(station.utilization)
                  }}
                />
              </div>

              <div className="station-metrics">
                <div className="metric">
                  <p className="metric-label">Revenue</p>
                  <p className="metric-value">₹{(station.revenue / 1000).toFixed(1)}K</p>
                </div>
                <div className="metric">
                  <p className="metric-label">Sessions</p>
                  <p className="metric-value">{station.sessions}</p>
                </div>
                <div className="metric">
                  <p className="metric-label">Station ID</p>
                  <p className="metric-value">{station.id}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Station Details */}
      {selectedStation && (
        <div className="station-details-panel">
          <div className="panel-header">
            <h2>{selectedStation.name}</h2>
            <button 
              className="btn-close-panel"
              onClick={() => setSelectedStation(null)}
            >
              Close
            </button>
          </div>

          <div className="panel-content">
            <div className="detail-row">
              <span className="detail-label">Station ID:</span>
              <span className="detail-value">{selectedStation.id}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Location:</span>
              <span className="detail-value">{selectedStation.location}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Status:</span>
              <span className="detail-value">
                <span 
                  className="status-pill"
                  style={{ 
                    background: getStatusColor(selectedStation.status) + '20',
                    color: getStatusColor(selectedStation.status)
                  }}
                >
                  {getStatusIcon(selectedStation.status)}
                  {selectedStation.status}
                </span>
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Total Chargers:</span>
              <span className="detail-value">{selectedStation.chargers.total}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Available:</span>
              <span className="detail-value" style={{ color: '#4CAF50', fontWeight: 600 }}>
                {selectedStation.chargers.available}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Occupied:</span>
              <span className="detail-value" style={{ color: '#FF9800', fontWeight: 600 }}>
                {selectedStation.chargers.occupied}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Under Maintenance:</span>
              <span className="detail-value" style={{ color: '#F44336', fontWeight: 600 }}>
                {selectedStation.chargers.maintenance}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Utilization Rate:</span>
              <span className="detail-value">
                <span style={{ color: getUtilizationColor(selectedStation.utilization), fontWeight: 700 }}>
                  {selectedStation.utilization}%
                </span>
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Total Revenue:</span>
              <span className="detail-value">₹{selectedStation.revenue.toLocaleString()}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Charging Sessions:</span>
              <span className="detail-value">{selectedStation.sessions}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Coordinates:</span>
              <span className="detail-value">
                {selectedStation.coordinates.lat}, {selectedStation.coordinates.lng}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Urjaa;
