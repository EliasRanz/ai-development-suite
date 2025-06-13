import { RefreshCw, Wifi, WifiOff, Clock } from 'lucide-react';

interface StatusIndicatorProps {
  lastUpdated: Date | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

export default function StatusIndicator({ 
  lastUpdated, 
  loading, 
  error, 
  onRefresh 
}: StatusIndicatorProps) {
  const formatLastUpdated = (date: Date | null) => {
    if (!date) return 'Never';
    
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
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
    return 'text-green-500';
  };

  const getStatusIcon = () => {
    if (error) return <WifiOff className="w-4 h-4" />;
    if (loading) return <RefreshCw className="w-4 h-4 animate-spin" />;
    return <Wifi className="w-4 h-4" />;
  };

  return (
    <div className="flex items-center space-x-2 text-sm text-gray-600">
      <button
        onClick={onRefresh}
        className={`flex items-center space-x-1 px-2 py-1 rounded hover:bg-gray-100 transition-colors ${getStatusColor()}`}
        title={error ? `Error: ${error}` : 'Click to refresh'}
      >
        {getStatusIcon()}
        <span className="hidden sm:inline">
          {error ? 'Offline' : loading ? 'Updating...' : 'Live'}
        </span>
      </button>
      
      {lastUpdated && !loading && (
        <div className="flex items-center space-x-1 text-gray-500">
          <Clock className="w-3 h-3" />
          <span className="text-xs">
            {formatLastUpdated(lastUpdated)}
          </span>
        </div>
      )}
    </div>
  );
}
