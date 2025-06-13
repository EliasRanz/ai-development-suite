import { useState, useCallback } from 'react';
import { Task } from '../types';

interface OptimisticUpdate {
  id: string;
  type: 'create' | 'update' | 'delete';
  taskId?: number;
  originalTask?: Task;
  optimisticTask?: Task;
  timestamp: number;
}

export function useOptimisticUpdates(tasks: Task[]) {
  const [pendingUpdates, setPendingUpdates] = useState<OptimisticUpdate[]>([]);

  const addOptimisticUpdate = useCallback((update: Omit<OptimisticUpdate, 'id' | 'timestamp'>) => {
    const optimisticUpdate: OptimisticUpdate = {
      ...update,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: Date.now()
    };
    
    setPendingUpdates(prev => [...prev, optimisticUpdate]);
    return optimisticUpdate.id;
  }, []);

  const removeOptimisticUpdate = useCallback((id: string) => {
    setPendingUpdates(prev => prev.filter(u => u.id !== id));
  }, []);

  const clearOptimisticUpdates = useCallback(() => {
    setPendingUpdates([]);
  }, []);

  // Apply optimistic updates to tasks
  const getOptimisticTasks = useCallback(() => {
    let optimisticTasks = [...tasks];
    
    pendingUpdates.forEach(update => {
      switch (update.type) {
        case 'create':
          if (update.optimisticTask) {
            optimisticTasks.push(update.optimisticTask);
          }
          break;
          
        case 'update':
          if (update.taskId && update.optimisticTask) {
            const index = optimisticTasks.findIndex(t => t.id === update.taskId);
            if (index !== -1) {
              optimisticTasks[index] = update.optimisticTask;
            }
          }
          break;
          
        case 'delete':
          if (update.taskId) {
            optimisticTasks = optimisticTasks.filter(t => t.id !== update.taskId);
          }
          break;
      }
    });
    
    return optimisticTasks;
  }, [tasks, pendingUpdates]);

  // Auto-cleanup old pending updates (after 30 seconds)
  useState(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setPendingUpdates(prev => 
        prev.filter(update => now - update.timestamp < 30000)
      );
    }, 5000);
    
    return () => clearInterval(interval);
  });

  return {
    optimisticTasks: getOptimisticTasks(),
    pendingUpdates,
    addOptimisticUpdate,
    removeOptimisticUpdate,
    clearOptimisticUpdates
  };
}

export default useOptimisticUpdates;
