import { useState } from 'react';
import { Task, Project } from './types';
import { api } from './api';
import RealTimeProvider, { useRealTime } from './hooks/useRealTime';
import ProjectSelector from './components/ProjectSelector';
import KanbanBoard from './components/KanbanBoard';
import TaskModal from './components/TaskModal';
import Header from './components/Header';
import LoadingSpinner from './components/LoadingSpinner';
import { Plus, BarChart3 } from 'lucide-react';

function AppContent() {
  const { data, loading, error } = useRealTime();
  const { projects, tasks, statusValues, priorityValues, selectedProject } = data;
  const { setSelectedProject } = useRealTime();
  
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [currentView, setCurrentView] = useState<'kanban' | 'dashboard'>('kanban');
  const [apiError, setApiError] = useState<string | null>(null);

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
      // The real-time provider will automatically refresh the tasks
      setShowTaskModal(false);
      setApiError(null);
    } catch (err) {
      setApiError(err instanceof Error ? err.message : 'Failed to create task');
    }
  };

  const handleUpdateTask = async (taskData: {
    title: string;
    description: string;
    priority: string;
    status: string;
  }) => {
    if (!editingTask) return;

    try {
      await api.updateTask(editingTask.id, taskData);
      // The real-time provider will automatically refresh the tasks
      setEditingTask(null);
      setShowTaskModal(false);
      setApiError(null);
    } catch (err) {
      setApiError(err instanceof Error ? err.message : 'Failed to update task');
    }
  };

  const handleProjectChange = (project: Project) => {
    setSelectedProject(project);
  };

  if (loading && projects.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  const displayError = error?.message || apiError;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        currentView={currentView}
        onViewChange={setCurrentView}
        selectedProject={selectedProject}
      />

      {displayError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mx-6 mt-4">
          {displayError}
          <button
            onClick={() => {
              setApiError(null);
            }}
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

        {selectedProject && currentView === 'kanban' && (
          <KanbanBoard
            tasks={tasks}
            statusValues={statusValues}
            priorityValues={priorityValues}
            onEditTask={(task: Task) => {
              setEditingTask(task);
              setShowTaskModal(true);
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

export default function App() {
  return (
    <RealTimeProvider refreshInterval={5000}>
      <AppContent />
    </RealTimeProvider>
  );
}
