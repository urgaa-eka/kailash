/**
 * KAILASH API Hooks
 * React Query hooks for data fetching
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

// Base API URL from environment
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

// Axios instance with interceptors
const api = axios.create({
  baseURL: API_BASE_URL
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = useAuthStore.getState().refreshToken;
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          useAuthStore.getState().updateToken(access_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          useAuthStore.getState().logout();
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// === AUTH HOOKS ===

export const useLogin = () => useMutation({
  mutationFn: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  }
});

export const useCurrentUser = () => useQuery({
  queryKey: ['currentUser'],
  queryFn: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
  enabled: useAuthStore.getState().isAuthenticated
});

export const usePermissions = () => useQuery({
  queryKey: ['permissions'],
  queryFn: async () => {
    const response = await api.get('/api/auth/permissions');
    return response.data;
  },
  enabled: useAuthStore.getState().isAuthenticated
});

// === DEPARTMENT HOOKS ===

export const useDepartments = () => useQuery({
  queryKey: ['departments'],
  queryFn: async () => {
    const response = await api.get('/api/departments');
    return response.data;
  }
});

export const useDepartmentDetails = (departmentId) => useQuery({
  queryKey: ['department', departmentId],
  queryFn: async () => {
    const response = await api.get(`/api/departments/${departmentId}`);
    return response.data;
  },
  enabled: !!departmentId
});

// === GUARDIAN HOOKS ===

export const useGuardianStatus = () => useQuery({
  queryKey: ['guardians', 'status'],
  queryFn: async () => {
    const response = await api.get('/api/guardians/status');
    return response.data;
  },
  refetchInterval: 30000 // Refresh every 30 seconds
});

export const useGuardianReport = (guardianName) => useQuery({
  queryKey: ['guardian', guardianName, 'report'],
  queryFn: async () => {
    const response = await api.get(`/api/guardians/${guardianName}/report`);
    return response.data;
  },
  enabled: !!guardianName
});

// === AUTOMOBILE PRICING HOOKS ===

export const usePricingTable = (vehicleType) => useQuery({
  queryKey: ['pricing', vehicleType],
  queryFn: async () => {
    const response = await api.get(`/api/automobile/pricing/table/${vehicleType}`);
    return response.data;
  },
  enabled: !!vehicleType,
  staleTime: 5 * 60 * 1000 // 5 minutes
});

export const useUniformPrice = (serviceType, vehicleType, region) => useQuery({
  queryKey: ['uniformPrice', serviceType, vehicleType, region],
  queryFn: async () => {
    const params = { service_type: serviceType, vehicle_type: vehicleType };
    if (region) params.region = region;
    const response = await api.get('/api/automobile/pricing/uniform', { params });
    return response.data;
  },
  enabled: !!serviceType && !!vehicleType
});

export const usePricingTrends = (serviceType, days = 30) => useQuery({
  queryKey: ['pricingTrends', serviceType, days],
  queryFn: async () => {
    const response = await api.get(`/api/automobile/pricing/trends/${serviceType}`, {
      params: { days }
    });
    return response.data;
  },
  enabled: !!serviceType
});

export const useMarketInsights = (vehicleType) => useQuery({
  queryKey: ['marketInsights', vehicleType],
  queryFn: async () => {
    const response = await api.get(`/api/automobile/market/insights/${vehicleType}`);
    return response.data;
  },
  enabled: !!vehicleType
});

export const useAddMarketData = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/api/automobile/market/data', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pricing'] });
      queryClient.invalidateQueries({ queryKey: ['marketInsights'] });
    }
  });
};

export const useSyncGSTData = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (days = 30) => {
      const response = await api.post('/api/automobile/gst/sync', null, {
        params: { days }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pricing'] });
      queryClient.invalidateQueries({ queryKey: ['gstAnalysis'] });
    }
  });
};

export const useGSTAnalysis = (filters = {}) => useQuery({
  queryKey: ['gstAnalysis', filters],
  queryFn: async () => {
    const response = await api.get('/api/automobile/gst/analysis', {
      params: filters
    });
    return response.data;
  }
});

// === CHAT/GANESHA HOOKS ===

export const useConversations = () => useQuery({
  queryKey: ['conversations'],
  queryFn: async () => {
    const response = await api.get('/api/conversations');
    return response.data;
  }
});

export const useSendMessage = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ message, conversationId }) => {
      const response = await api.post('/api/ganesha/orchestrate', {
        user_message: message,
        conversation_id: conversationId
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    }
  });
};

// === ANALYTICS HOOKS ===

export const useAnalytics = (period = '7d') => useQuery({
  queryKey: ['analytics', period],
  queryFn: async () => {
    const response = await api.get('/api/analytics', {
      params: { period }
    });
    return response.data;
  },
  refetchInterval: 60000 // Refresh every minute
});

// Export the api instance for custom requests
export { api };
