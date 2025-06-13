import { createContext, useContext, ReactNode, useState, useEffect } from 'react';
import { Project, Task, StatusValue, PriorityValue } from '../types';
import { api } from '../api';
import { useAutoRefresh } from './useAutoRefresh';
import { usePageVisibility } from './usePageVisibility';

interface RealTimeData {
  projects: Project[];
  tasks: Task[];
  statusValues: StatusValue[];
  priorityValues: PriorityValue[];
  selectedProject: Project | null;
}

interface RealTimeContextType {
  data: RealTimeData;
  loading: boolean;
  error: Error | null;
  lastUpdated: Date | null;
  refresh: () => void;
  setSelectedProject: (project: Project | null) => void;
}

const RealTimeContext = createContext<RealTimeContextType | null>(null);

interface RealTimeProviderProps {
  children: ReactNode;
  refreshInterval?: number;
}

export function RealTimeProvider({ children, refreshInterval = 5000 }: RealTimeProviderProps) {
  const isVisible = usePageVisibility();
  
  // Auto-refresh projects, status values, and priority values
  const {
    data: projectsData,
    loading: projectsLoading,
    error: projectsError,
    refresh: refreshProjects
  } = useAutoRefresh(
    () => api.getProjects(),
    { interval: refreshInterval * 2, enabled: isVisible } // Projects update less frequently
  );

  const {
    data: statusValues,
    loading: statusLoading,
    error: statusError,
    refresh: refreshStatus
  } = useAutoRefresh(
    () => api.getStatusValues(),
    { interval: refreshInterval * 4, enabled: isVisible } // Status values rarely change
  );

  const {
    data: priorityValues,
    loading: priorityLoading,
    error: priorityError,
    refresh: refreshPriority
  } = useAutoRefresh(
    () => api.getPriorityValues(),
    { interval: refreshInterval * 4, enabled: isVisible } // Priority values rarely change
  );

  // For now, we'll manage selectedProject locally
  // In a full implementation, this could be synced across tabs
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  // Auto-refresh tasks for the selected project
  const {
    data: tasks,
    loading: tasksLoading,
    error: tasksError,
    lastUpdated,
    refresh: refreshTasks
  } = useAutoRefresh(
    () => selectedProject ? api.getTasks(selectedProject.id) : Promise.resolve([]),
    { 
      interval: refreshInterval, 
      enabled: isVisible && !!selectedProject 
    }
  );

  // Set initial selected project when projects load
  useEffect(() => {
    if (projectsData && projectsData.length > 0 && !selectedProject) {
      setSelectedProject(projectsData[0]);
    }
  }, [projectsData, selectedProject]);

  const data: RealTimeData = {
    projects: projectsData || [],
    tasks: tasks || [],
    statusValues: statusValues || [],
    priorityValues: priorityValues || [],
    selectedProject
  };

  const loading = projectsLoading || statusLoading || priorityLoading || tasksLoading;
  const error = projectsError || statusError || priorityError || tasksError;

  const refresh = () => {
    refreshProjects();
    refreshStatus();
    refreshPriority();
    refreshTasks();
  };

  const contextValue: RealTimeContextType = {
    data,
    loading,
    error,
    lastUpdated,
    refresh,
    setSelectedProject
  };

  return (
    <RealTimeContext.Provider value={contextValue}>
      {children}
    </RealTimeContext.Provider>
  );
}

export function useRealTime() {
  const context = useContext(RealTimeContext);
  if (!context) {
    throw new Error('useRealTime must be used within a RealTimeProvider');
  }
  return context;
}

export default RealTimeProvider;
