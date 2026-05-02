/**
 * KAILASH Auth Store
 * Zustand state management for authentication
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      is2FAEnabled: false,
      
      // Actions
      login: (tokens, user) => {
        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token || tokens.access_token,
          user,
          isAuthenticated: true,
          is2FAEnabled: user?.is_2fa_enabled || false
        });
      },
      
      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          is2FAEnabled: false
        });
        // Clear from localStorage
        localStorage.removeItem('kailash-auth');
      },
      
      setUser: (user) => {
        set({
          user,
          is2FAEnabled: user?.is_2fa_enabled || false
        });
      },
      
      updateToken: (accessToken) => {
        set({ accessToken });
      },
      
      set2FAStatus: (enabled) => {
        set({ is2FAEnabled: enabled });
      },
      
      // Getters
      getToken: () => get().accessToken,
      getUser: () => get().user,
      isLoggedIn: () => get().isAuthenticated
    }),
    {
      name: 'kailash-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
        is2FAEnabled: state.is2FAEnabled
      })
    }
  )
);
