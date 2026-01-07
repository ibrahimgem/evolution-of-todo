/**
 * Custom hook to sync API client with auth token
 * T021: Ensure API client always has current JWT token
 */

import { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../lib/api-client';

/**
 * Sync API client with authentication token
 * Call this hook in components that need to make authenticated API calls
 */
export function useApiClient() {
  const { token } = useAuth();

  useEffect(() => {
    // Update API client whenever token changes
    apiClient.setToken(token);
  }, [token]);

  return apiClient;
}
