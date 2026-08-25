import React, { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import './GaneshaAnalytics.css';

const GaneshaAnalytics = () => {
  const [stats, setStats] = useState({
    totalAgents: 36,
    ragVectors: 851,
    sessionQueries: 0,
    monthlyCost: 250
  });

  const [tierDistribution] = useState({
    sonnet: 30,
    haiku: 70
  });

  const [agents] = useState([
    { name: 'GANESHA', tier: 'Sonnet 4', product: 'KAILASH', status: 'active' },
    { name: 'VISHWAKARMA', tier: 'Sonnet 4', product: 'KAILASH', status: 'active' },
    { name: 'SURYA', tier: 'Sonnet 4', product: 'URGAA', status: 'active' },
    { name: 'TVASHTA', tier: 'Haiku', product: 'GSTSAAS', status: 'active' },
    { name: 'KARTIKEYA', tier: 'Haiku', product: 'IGNITION', status: 'active' },
    { name: 'LAKSHMI', tier: 'Sonnet 4', product: 'KAILASH', status: 'active' },
    { name: 'KUBERA', tier: 'Haiku', product: 'KAILASH', status: 'active' },
    { name: 'KAMADEVA', tier: 'Haiku', product: 'KAILASH', status: 'active' },
    { name: 'BRIHASPATI', tier: 'Haiku', product: 'KAILASH', status: 'active' },
    { name: 'INDRA', tier: 'Sonnet 4', product: 'KAILASH', status: 'active' }
  ]);

  const refreshData = () => {
    setStats(prev => ({
      ...prev,
      sessionQueries: prev.sessionQueries + Math.floor(Math.random() * 5)
    }));
  };

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <h1>GANESHA Analytics Dashboard</h1>
        <button onClick={refreshData} className="refresh-btn">
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.totalAgents}</div>
          <div className="stat-label">Total Agents</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.ragVectors}</div>
          <div className="stat-label">RAG Vectors</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.sessionQueries}</div>
          <div className="stat-label">Session Queries</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">${stats.monthlyCost}</div>
          <div className="stat-label">Est. Monthly Cost</div>
        </div>
      </div>

      <div className="tier-distribution">
        <h2>C5 Tier Distribution</h2>
        <div className="tier-bar">
          <div className="tier-segment sonnet" style={{ width: `${tierDistribution.sonnet}%` }}>
            Sonnet 4 ({tierDistribution.sonnet}%)
          </div>
          <div className="tier-segment haiku" style={{ width: `${tierDistribution.haiku}%` }}>
            Haiku ({tierDistribution.haiku}%)
          </div>
        </div>
      </div>

      <div className="agents-table">
        <h2>Agent Registry</h2>
        <table>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Model Tier</th>
              <th>Product</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {agents.map((agent, idx) => (
              <tr key={idx}>
                <td>{agent.name}</td>
                <td>
                  <span className={`tier-badge ${agent.tier.includes('Sonnet') ? 'sonnet' : 'haiku'}`}>
                    {agent.tier}
                  </span>
                </td>
                <td>{agent.product}</td>
                <td>
                  <span className="status-badge active">{agent.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default GaneshaAnalytics;
