import { useState, useEffect } from 'react';
import { RefreshCw, Wifi, WifiOff, Clock } from 'lucide-react';

interface StatusIndicatorProps {
  lastUpdated: Date | null;
  loading: boolean;
  error: string | null;
  isLiveUpdateEnabled: boolean;
  onRefresh: () => void;
  onToggleLiveUpdate: () => void;
}

export default function StatusIndicator({ 
  lastUpdated, 
  loading, 
  error, 
  isLiveUpdateEnabled,
  onRefresh,
  onToggleLiveUpdate
}: StatusIndicatorProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update current time every second to keep "time ago" fresh
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatLastUpdated = (date: Date | null) => {
    if (!date) return 'Never';
    
    const diff = currentTime.getTime() - date.getTime();
    const seconds = Math.max(0, Math.floor(diff / 1000)); // Prevent negative values
    const minutes = Math.floor(seconds / 60);
    
    if (seconds < 60) {
      return `${seconds}s ago`;
    } else if (minutes < 60) {
      return `${minutes}m ago`;
    } else {
      const hours = Math.floor(minutes / 60);
      return `${hours}h ago`;
    }
  };

  const getStatusColor = () => {
    if (error) return 'text-red-500';
    if (loading) return 'text-blue-500';
    if (!isLiveUpdateEnabled) return 'text-gray-500';
    return 'text-green-500';
  };

  const getStatusIcon = () => {
    if (error) return <WifiOff className="w-4 h-4" />;
    if (loading) return <RefreshCw className="w-4 h-4 animate-spin" />;
    if (!isLiveUpdateEnabled) return <WifiOff className="w-4 h-4" />;
    return <Wifi className="w-4 h-4" />;
  };

  const getStatusText = () => {
    if (error) return 'Offline';
    if (!isLiveUpdateEnabled) return 'Offline';
    return 'Live'; // Always show "Live" when enabled, even during loading
  };

  const getTooltipText = () => {
    if (error) return `Error: ${error}. Click to retry.`;
    if (!isLiveUpdateEnabled) return 'Live updates disabled. Click to enable.';
    return 'Live updates enabled. Click to disable.';
  };

  return (
    <div className="flex items-center space-x-2 text-sm text-gray-600">
      <button
        onClick={error ? onRefresh : onToggleLiveUpdate}
        className={`flex items-center space-x-1 px-2 py-1 rounded hover:bg-gray-100 transition-colors ${getStatusColor()}`}
        title={getTooltipText()}
      >
        {getStatusIcon()}
        <span className="hidden sm:inline min-w-0">
          {getStatusText()}
        </span>
      </button>
      
      {lastUpdated && (
        <div className="flex items-center space-x-1 text-gray-500 min-w-0">
          <Clock className="w-3 h-3" />
          <span className="text-xs whitespace-nowrap">
            {formatLastUpdated(lastUpdated)}
          </span>
        </div>
      )}
    </div>
  );
}
