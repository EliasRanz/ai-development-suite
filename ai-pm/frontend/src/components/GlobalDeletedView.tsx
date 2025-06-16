import { useState, useEffect } from 'react';
import { Task, Project } from '../types';
import { api } from '../api';
import { RotateCcw, Trash2, Calendar, AlertCircle } from 'lucide-react';
import RecoveryDialog from './RecoveryDialog';
import Pagination from './Pagination';

interface GlobalDeletedViewProps {
  projects?: Project[];
}

export default function GlobalDeletedView({ projects = [] }: GlobalDeletedViewProps) {
  const [deletedTasks, setDeletedTasks] = useState<Task[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recoveryDialogOpen, setRecoveryDialogOpen] = useState(false);
  const [taskToRecover, setTaskToRecover] = useState<Task | null>(null);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10); // 10 tasks per page

  // Load deleted tasks
  useEffect(() => {
    const loadDeletedTasks = async () => {
      try {
        setLoading(true);
        setError(null);
        const tasks = await api.getDeletedTasks(selectedProjectId || undefined);
        setDeletedTasks(tasks);
      } catch (err) {
        console.error('Failed to load deleted tasks:', err);
        setError('Failed to load deleted tasks');
      } finally {
        setLoading(false);
      }
    };

    loadDeletedTasks();
    setCurrentPage(1); // Reset to first page when project filter changes
  }, [selectedProjectId]);

  const handleRecoverTask = (task: Task) => {
    setTaskToRecover(task);
    setRecoveryDialogOpen(true);
  };

  const handleConfirmRecover = async (taskId: number, status: string, priority?: string) => {
    try {
      await api.recoverTask(taskId, status);
      // If priority is different, update it after recovery
      if (priority && priority !== taskToRecover?.priority) {
        await api.updateTask(taskId, { priority });
      }
      // Remove the recovered task from the list
      setDeletedTasks(prev => prev.filter(task => task.id !== taskId));
      setRecoveryDialogOpen(false);
      setTaskToRecover(null);
    } catch (err) {
      console.error('Failed to recover task:', err);
      // You might want to show a toast notification here
    }
  };

  const handleProjectChange = (projectId: string) => {
    setSelectedProjectId(projectId === 'all' ? null : parseInt(projectId));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  // Pagination calculations
  const totalItems = deletedTasks.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentTasks = deletedTasks.slice(startIndex, endIndex);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Trash2 className="w-6 h-6 text-red-600" />
            <h2 className="text-xl font-semibold text-gray-900">Deleted Tasks</h2>
            {totalItems > 0 && (
              <span className="bg-red-100 text-red-800 text-sm font-medium px-2 py-1 rounded-full">
                {totalItems} total
              </span>
            )}
          </div>
          
          {/* Project Filter */}
          <div className="flex items-center space-x-3">
            <label htmlFor="project-filter" className="text-sm font-medium text-gray-700">
              Filter by project:
            </label>
            <select
              id="project-filter"
              value={selectedProjectId || 'all'}
              onChange={(e) => handleProjectChange(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Projects</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-500">Loading deleted tasks...</div>
          </div>
        ) : deletedTasks.length === 0 ? (
          <div className="text-center py-12">
            <Trash2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No deleted tasks</h3>
            <p className="text-gray-500">
              {selectedProjectId 
                ? `No deleted tasks found for the selected project.`
                : 'No deleted tasks found across all projects.'
              }
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {currentTasks.map((task) => (
              <div
                key={task.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="font-medium text-gray-900">{task.title}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(task.priority)}`}>
                        {task.priority}
                      </span>
                      {task.project_name && (
                        <span className="px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded-full">
                          {task.project_name}
                        </span>
                      )}
                    </div>
                    
                    {task.description && (
                      <p className="text-gray-600 text-sm mb-3">{task.description}</p>
                    )}
                    
                    {task.deletion_reason && (
                      <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex items-start space-x-2">
                          <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-sm font-semibold text-red-800">Deletion Reason:</p>
                            <p className="text-sm text-red-700">{task.deletion_reason}</p>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3" />
                        <span>Deleted: {task.deleted_at ? formatDate(task.deleted_at) : 'Unknown'}</span>
                      </div>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => handleRecoverTask(task)}
                    className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                    title="Recover this task"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>Recover</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Pagination */}
        {totalItems > 0 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
            itemsPerPage={itemsPerPage}
            totalItems={totalItems}
          />
        )}
      </div>

      {/* Recovery Dialog */}
      {taskToRecover && (
        <RecoveryDialog
          task={taskToRecover}
          isOpen={recoveryDialogOpen}
          onClose={() => {
            setRecoveryDialogOpen(false);
            setTaskToRecover(null);
          }}
          onRecover={handleConfirmRecover}
        />
      )}
    </div>
  );
}
