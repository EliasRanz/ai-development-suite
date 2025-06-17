import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Project, Task, StatusValue, PriorityValue, UpdateTaskRequest } from './types';
import { api } from './api';
import { usePolling } from './hooks/usePolling';
import ProjectBoard from './components/ProjectBoard';
import TaskModal from './components/TaskModal';
import TaskPage from './components/TaskPage';
import LoadingSpinner from './components/LoadingSpinner';
import StatusIndicator from './components/StatusIndicator';
import { Plus, BarChart3 } from 'lucide-react';

interface AppProps {
  selectedProject: Project | null;
}

export default function App({ selectedProject }: AppProps) {
  const navigate = useNavigate();
  const { view, taskId } = useParams();
  
  const [tasks, setTasks] = useState<Task[]>([]);
  const [statusValues, setStatusValues] = useState<StatusValue[]>([]);
  const [priorityValues, setPriorityValues] = useState<PriorityValue[]>([]);
  const [loading, setLoading] = useState(true);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isTaskEditMode, setIsTaskEditMode] = useState(false);
  const [isLiveUpdateEnabled, setIsLiveUpdateEnabled] = useState(true);

  // Determine current view from URL, default to project view (kanban)
  const currentView = view || 'kanban';
  const showTaskView = !!taskId;

  // Utility function to create URL-friendly slug from project name
  const createProjectSlug = (project: Project): string => {
    return project.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  // Load specific task when taskId is in URL
  useEffect(() => {
    if (taskId && tasks.length > 0) {
      const task = tasks.find(t => t.id.toString() === taskId);
      if (task) {
        setEditingTask(task);
      }
    } else if (!taskId) {
      setEditingTask(null);
    }
  }, [taskId, tasks]);

  const loadTasks = useCallback(async () => {
    if (!selectedProject) return;
    try {
      setTasksLoading(true);
      const tasksData = await api.getTasks(selectedProject.id);
      setTasks(tasksData || []); // Ensure we never set null/undefined
      setLastUpdated(new Date());
      setError(null); // Clear any previous errors
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
      setTasks([]); // Set empty array on error to prevent null issues
    } finally {
      setTasksLoading(false);
    }
  }, [selectedProject]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [statusData, priorityData] = await Promise.all([
        api.getStatusValues(),
        api.getPriorityValues(),
      ]);
      setStatusValues(statusData);
      setPriorityValues(priorityData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh tasks every 5 seconds when project is selected and live updates are enabled
  usePolling(loadTasks, { 
    enabled: !!selectedProject && !loading && isLiveUpdateEnabled, 
    interval: 5000 
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      loadTasks();
    }
  }, [selectedProject, loadTasks]);

  const handleCreateTask = async (taskData: {
    title: string;
    description: string;
    priority: string;
    status: string;
  }) => {
    if (!selectedProject) return;

    try {
      await api.createTask({
        project_id: selectedProject.id,
        ...taskData,
      });
      loadTasks();
      setShowTaskModal(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    }
  };

  const handleUpdateTask = async (taskData: UpdateTaskRequest) => {
    if (!editingTask) return;

    try {
      await api.updateTask(editingTask.id, taskData);
      await loadTasks(); // Reload tasks
      setShowTaskModal(false);
      setEditingTask(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    }
  };

  const handleManualRefresh = () => {
    if (selectedProject) {
      loadTasks();
    }
  };

  const toggleLiveUpdates = () => {
    setIsLiveUpdateEnabled(prev => !prev);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <>
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
          {error}
          <button
            onClick={() => setError(null)}
            className="float-right text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      )}

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          {selectedProject && (
            <h2 className="text-xl font-semibold text-gray-900">
              {selectedProject.name}
            </h2>
          )}
        </div>

        <div className="flex items-center space-x-3">
          <StatusIndicator
            lastUpdated={lastUpdated}
            loading={tasksLoading}
            error={error}
            isLiveUpdateEnabled={isLiveUpdateEnabled}
            onRefresh={handleManualRefresh}
            onToggleLiveUpdate={toggleLiveUpdates}
          />
          {showTaskView && editingTask ? (
            <button
              onClick={() => {
                setIsTaskEditMode(true);
                setShowTaskModal(true);
              }}
              className="flex items-center space-x-2 btn-primary"
            >
              <Plus className="w-4 h-4" />
              <span>Edit Task</span>
            </button>
          ) : (
            <button
              onClick={() => {
                setEditingTask(null);
                setShowTaskModal(true);
              }}
              className="flex items-center space-x-2 btn-primary"
            >
              <Plus className="w-4 h-4" />
              <span>New Task</span>
            </button>
          )}
        </div>
      </div>

      {showTaskView && editingTask ? (
        <TaskPage
          task={editingTask}
          statusValues={statusValues}
          priorityValues={priorityValues}
          onSave={handleUpdateTask}
          onBack={() => {
            if (selectedProject) {
              const slug = createProjectSlug(selectedProject);
              navigate(`/projects/${slug}`);
            }
          }}
          isEditMode={isTaskEditMode}
          onEditModeChange={setIsTaskEditMode}
        />
      ) : (
        <>
          {selectedProject && currentView === 'kanban' && (
            <ProjectBoard
              tasks={tasks}
              statusValues={statusValues}
              priorityValues={priorityValues}
              onViewTask={(task: Task) => {
                if (selectedProject) {
                  const slug = createProjectSlug(selectedProject);
                  navigate(`/projects/${slug}/tasks/${task.id}`);
                }
              }}
            />
          )}

          {currentView === 'dashboard' && (
            <div className="text-center py-12">
              <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-500">Dashboard Coming Soon</h3>
              <p className="text-gray-400">Analytics and project insights will be available here.</p>
            </div>
          )}
        </>
      )}

      {showTaskModal && (
        <TaskModal
          task={editingTask}
          statusValues={statusValues}
          priorityValues={priorityValues}
          onSave={editingTask ? handleUpdateTask : handleCreateTask}
          onClose={() => {
            setShowTaskModal(false);
            setEditingTask(null);
          }}
        />
      )}
    </>
  );
}
