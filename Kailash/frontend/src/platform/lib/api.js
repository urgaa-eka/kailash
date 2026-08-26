// API utility functions for Executive Dashboard
const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

export const executiveAPI = {
  getKPIs: async () => {
    const response = await fetch(`${API_URL}/api/executive/kpis`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch KPIs');
    return { data: await response.json() };
  },

  getAlerts: async () => {
    const response = await fetch(`${API_URL}/api/executive/alerts`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch alerts');
    return { data: await response.json() };
  },

  getProjectHealth: async () => {
    const response = await fetch(`${API_URL}/api/executive/project-health`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch project health');
    return { data: await response.json() };
  },

  getFinancial: async () => {
    const response = await fetch(`${API_URL}/api/executive/financial`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch financial data');
    return { data: await response.json() };
  },

  getOpsHealth: async () => {
    const response = await fetch(`${API_URL}/api/executive/ops-health`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch ops health');
    return { data: await response.json() };
  }
};

export const stationsAPI = {
  getCitiesSummary: async () => {
    const response = await fetch(`${API_URL}/api/stations/cities-summary`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch cities summary');
    return { data: await response.json() };
  }
};
