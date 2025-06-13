import { useState, useEffect } from 'react';
import { Project, Task, StatusValue, PriorityValue } from './types';
import { api } from './api';
import ProjectSelector from './components/ProjectSelector';
import KanbanBoard from './components/KanbanBoard';
import TaskModal from './components/TaskModal';
import Header from './components/Header';
import LoadingSpinner from './components/LoadingSpinner';
import { Plus, BarChart3 } from 'lucide-react';

export default function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [statusValues, setStatusValues] = useState<StatusValue[]>([]);
  const [priorityValues, setPriorityValues] = useState<PriorityValue[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [currentView, setCurrentView] = useState<'kanban' | 'dashboard'>('kanban');

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      loadTasks();
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

  const loadTasks = async () => {
    if (!selectedProject) return;
    try {
      const tasksData = await api.getTasks(selectedProject.id);
      setTasks(tasksData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    }
  };

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

  const handleUpdateTask = async (taskData: {
    title: string;
    description: string;
    priority: string;
    status: string;
  }) => {
    if (!editingTask) return;

    try {
      await api.updateTask(editingTask.id, taskData);
      loadTasks();
      setEditingTask(null);
      setShowTaskModal(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    }
  };

  const handleProjectChange = (project: Project) => {
    setSelectedProject(project);
    setTasks([]);
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
