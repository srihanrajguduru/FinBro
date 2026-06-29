/**
 * --------------------------------------------------------
 * File: web/lib/store.ts
 * Purpose: Global Client State Management (Zustand)
 * Responsibilities: Handles global application state, authentication tokens
 *                   persisted to localStorage, current user information, and UI controls.
 * Author: Srihan Raj Guduru
 * --------------------------------------------------------
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "./api";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
}

/**
 * Hook for interacting with the global authentication store.
 * Manages JWT tokens, persistent session storage, and the current user profile.
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setTokens: (access, refresh) => {
        if (typeof window !== "undefined") {
          localStorage.setItem("access_token", access);
          localStorage.setItem("refresh_token", refresh);
        }
        set({ accessToken: access, refreshToken: refresh });
      },
      setUser: (user) => set({ user }),
      logout: () => {
        if (typeof window !== "undefined") {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
        set({ accessToken: null, refreshToken: null, user: null });
      },
    }),
    { name: "finbro-auth" }
  )
);

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

/**
 * Hook for global UI state variables (e.g. sidebar toggle status).
 */
export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));
