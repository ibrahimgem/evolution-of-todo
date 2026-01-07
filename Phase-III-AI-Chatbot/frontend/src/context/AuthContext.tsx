'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

/**
 * AuthContext - JWT token management
 * T019: Complete implementation with login, logout, and token validation
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * User information interface
 */
interface User {
  id: string;
  email: string;
  name: string | null;
}

/**
 * Login response from backend
 */
interface LoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * Auth context interface
 */
interface AuthContextType {
  token: string | null;
  setToken: (token: string | null) => void;
  isAuthenticated: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Parse JWT token to extract user information
 * @param token JWT token string
 * @returns Decoded token payload or null
 */
function parseJwt(token: string): { sub: string; exp: number } | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Failed to parse JWT:', error);
    return null;
  }
}

/**
 * Check if JWT token is expired
 * @param token JWT token string
 * @returns true if token is expired, false otherwise
 */
function isTokenExpired(token: string): boolean {
  const decoded = parseJwt(token);
  if (!decoded || !decoded.exp) {
    return true;
  }
  // Check if token expires in less than 5 minutes (buffer for API calls)
  return decoded.exp * 1000 < Date.now() + 5 * 60 * 1000;
}

/**
 * AuthProvider component - manages authentication state and JWT tokens
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Fetch user information from backend using JWT token
   */
  const fetchUserInfo = useCallback(async (authToken: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user info');
      }

      const userData = await response.json();
      setUser({
        id: String(userData.id),
        email: userData.email,
        name: userData.name,
      });
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      // Clear invalid token
      setTokenState(null);
      setUser(null);
      localStorage.removeItem('auth_token');
    }
  }, []);

  /**
   * Load token from localStorage and validate on mount
   */
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('auth_token');

      if (storedToken) {
        // Check if token is expired
        if (isTokenExpired(storedToken)) {
          console.log('Stored token is expired');
          localStorage.removeItem('auth_token');
          setIsLoading(false);
          return;
        }

        setTokenState(storedToken);
        await fetchUserInfo(storedToken);
      }

      setIsLoading(false);
    };

    initializeAuth();
  }, [fetchUserInfo]);

  /**
   * Set JWT token and persist to localStorage
   */
  const setToken = useCallback((newToken: string | null) => {
    setTokenState(newToken);
    if (newToken) {
      localStorage.setItem('auth_token', newToken);
    } else {
      localStorage.removeItem('auth_token');
    }
  }, []);

  /**
   * Login user with email and password
   * @throws Error if login fails
   */
  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Login failed');
      }

      const data: LoginResponse = await response.json();
      setToken(data.access_token);
      await fetchUserInfo(data.access_token);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  /**
   * Register new user with email, password, and optional name
   * @throws Error if registration fails
   */
  const register = async (email: string, password: string, name?: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Registration failed');
      }

      const data: LoginResponse = await response.json();
      setToken(data.access_token);
      await fetchUserInfo(data.access_token);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  /**
   * Logout user and clear authentication state
   */
  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, [setToken]);

  return (
    <AuthContext.Provider
      value={{
        token,
        setToken,
        isAuthenticated: !!token,
        user,
        login,
        register,
        logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Custom hook to access auth context
 * @throws Error if used outside AuthProvider
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
