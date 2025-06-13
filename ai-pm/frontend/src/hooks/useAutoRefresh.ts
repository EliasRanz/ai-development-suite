import { useState, useEffect, useCallback, useRef } from 'react';

interface UseAutoRefreshOptions {
  interval?: number; // in milliseconds
  enabled?: boolean;
  onError?: (error: Error) => void;
}

export function useAutoRefresh<T>(
  fetchFunction: () => Promise<T>,
  options: UseAutoRefreshOptions = {}
) {
  const {
    interval = 5000, // Default 5 seconds
    enabled = true,
    onError
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  const intervalRef = useRef<number | null>(null);
  const mountedRef = useRef(true);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const result = await fetchFunction();
      
      if (mountedRef.current) {
        setData(result);
        setLastUpdated(new Date());
        setLoading(false);
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      
      if (mountedRef.current) {
        setError(error);
        setLoading(false);
        onError?.(error);
      }
    }
  }, [fetchFunction, onError]);

  const startPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    if (enabled) {
      intervalRef.current = setInterval(() => {
        fetchData();
      }, interval);
    }
  }, [fetchData, interval, enabled]);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const refresh = useCallback(() => {
    fetchData();
  }, [fetchData]);

  // Initial fetch and start polling
  useEffect(() => {
    fetchData();
    startPolling();

    return () => {
      stopPolling();
    };
  }, [fetchData, startPolling, stopPolling]);

  // Update polling when enabled/interval changes
  useEffect(() => {
    if (enabled) {
      startPolling();
    } else {
      stopPolling();
    }
  }, [enabled, startPolling, stopPolling]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      stopPolling();
    };
  }, [stopPolling]);

  return {
    data,
    loading,
    error,
    lastUpdated,
    refresh,
    startPolling,
    stopPolling
  };
}

export default useAutoRefresh;
