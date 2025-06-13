import { useEffect, useRef } from 'react';

interface UsePollingOptions {
  enabled?: boolean;
  interval?: number;
}

export function usePolling(
  callback: () => void,
  { enabled = true, interval = 5000 }: UsePollingOptions = {}
) {
  const callbackRef = useRef(callback);
  const intervalRef = useRef<number | null>(null);

  // Update callback ref when it changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    intervalRef.current = window.setInterval(() => {
      callbackRef.current();
    }, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, interval]);

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const startPolling = () => {
    if (enabled && !intervalRef.current) {
      intervalRef.current = window.setInterval(() => {
        callbackRef.current();
      }, interval);
    }
  };

  return { stopPolling, startPolling };
}

export default usePolling;
