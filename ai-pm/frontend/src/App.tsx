import { useState, useEffect, useCallback } from 'react';
import { Project, Task, StatusValue, PriorityValue, CreateTaskRequest, UpdateTaskRequest } from './types';
import { api } from './api';
import { usePolling } from './hooks/usePolling';
import ProjectSelector from './components/ProjectSelector';
import KanbanBoard from './components/KanbanBoard';
import TaskModal from './components/TaskModal';
import TaskPage from './components/TaskPage';
import DeletedTasksView from './components/DeletedTasksView';
import Header from './components/Header';
import LoadingSpinner from './components/LoadingSpinner';
import StatusIndicator from './components/StatusIndicator';
import { Plus, BarChart3 } from 'lucide-react';

export default function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [statusValues, setStatusValues] = useState<StatusValue[]>([]);
  const [priorityValues, setPriorityValues] = useState<PriorityValue[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [currentView, setCurrentView] = useState<'kanban' | 'dashboard' | 'deleted'>('kanban');
  const [showTaskView, setShowTaskView] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const loadTasks = useCallback(async () => {
    if (!selectedProject) return;
    try {
      setTasksLoading(true);
      const tasksData = await api.getTasks(selectedProject.id);
      setTasks(tasksData);
      setLastUpdated(new Date());
      setError(null); // Clear any previous errors
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setTasksLoading(false);
    }
  }, [selectedProject]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [projectsData, statusData, priorityData] = await Promise.all([
        api.getProjects(),
        api.getStatusValues(),
        api.getPriorityValues(),
      ]);
      setProjects(projectsData);
      setStatusValues(statusData);
      setPriorityValues(priorityData);
      if (projectsData.length > 0 && !selectedProject) {
        setSelectedProject(projectsData[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh tasks every 5 seconds when project is selected
  usePolling(loadTasks, { 
    enabled: !!selectedProject && !loading, 
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

  const handleProjectChange = (project: Project) => {
    setSelectedProject(project);
    setTasks([]);
  };

  const handleManualRefresh = () => {
    if (selectedProject) {
      loadTasks();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        currentView={currentView}
        onViewChange={setCurrentView}
        selectedProject={selectedProject}
      />

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mx-6 mt-4">
          {error}
          <button
            onClick={() => setError(null)}
            className="float-right text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      )}

      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <ProjectSelector
              projects={projects}
              selectedProject={selectedProject}
              onProjectChange={handleProjectChange}
            />
          </div>

          <div className="flex items-center space-x-3">
            <StatusIndicator
              lastUpdated={lastUpdated}
              loading={tasksLoading}
              error={error}
              onRefresh={handleManualRefresh}
            />
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
          </div>
        </div>

        {showTaskView && editingTask ? (
          <TaskPage
            task={editingTask}
            statusValues={statusValues}
            priorityValues={priorityValues}
            onSave={handleUpdateTask}
            onBack={() => {
              setShowTaskView(false);
              setEditingTask(null);
            }}
          />
        ) : (
          <>
            {selectedProject && currentView === 'kanban' && (
              <KanbanBoard
                tasks={tasks}
                statusValues={statusValues}
                priorityValues={priorityValues}
                onViewTask={(task: Task) => {
                  setEditingTask(task);
                  setShowTaskView(true);
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

            {currentView === 'deleted' && (
              <DeletedTasksView
                selectedProjectId={selectedProject?.id}
                statusValues={statusValues}
                onTaskRecovered={loadTasks}
              />
            )}
          </>
        )}
      </div>

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
    </div>
  );
}
