import { useState, useEffect } from 'react';
import { Task, StatusValue } from '../types';
import { api } from '../api';
import { useToast } from './ToastProvider';
import { RotateCcw, Calendar, AlertCircle, Clock, User } from 'lucide-react';

interface DeletedTasksViewProps {
  selectedProjectId?: number;
  statusValues: StatusValue[];
  onTaskRecovered?: () => void;
}

export default function DeletedTasksView({ selectedProjectId, statusValues, onTaskRecovered }: DeletedTasksViewProps) {
  const [deletedTasks, setDeletedTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [recovering, setRecovering] = useState<number | null>(null);
  const { addToast } = useToast();

  const loadDeletedTasks = async () => {
    try {
      setLoading(true);
      const tasks = await api.getDeletedTasks(selectedProjectId);
      setDeletedTasks(tasks);
    } catch (error) {
      console.error('Failed to load deleted tasks:', error);
      addToast({ message: 'Failed to load deleted tasks', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDeletedTasks();
  }, [selectedProjectId]);

  const handleRecoverTask = async (task: Task, newStatus: string) => {
    try {
      setRecovering(task.id);
      await api.recoverTask(task.id, newStatus);
      addToast({ message: `Task "${task.title}" recovered successfully`, type: 'success' });
      loadDeletedTasks(); // Refresh the list
      onTaskRecovered?.(); // Notify parent to refresh main tasks
    } catch (error) {
      console.error('Failed to recover task:', error);
      addToast({ message: 'Failed to recover task', type: 'error' });
    } finally {
      setRecovering(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (deletedTasks.length === 0) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No deleted tasks</h3>
        <p className="text-gray-500">
          {selectedProjectId ? 'No deleted tasks found for this project.' : 'No deleted tasks found.'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 mb-6">
        <AlertCircle className="h-5 w-5 text-red-500" />
        <h2 className="text-xl font-semibold text-gray-900">Deleted Tasks</h2>
        <span className="bg-red-100 text-red-800 text-sm font-medium px-2 py-1 rounded-full">
          {deletedTasks.length}
        </span>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
        <div className="flex items-start space-x-2">
          <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5" />
          <div>
            <p className="text-sm text-amber-800 font-medium">Deleted Tasks Recovery</p>
            <p className="text-sm text-amber-700 mt-1">
              These tasks have been soft-deleted and can be recovered. Select a status to restore a task back to the main board.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4">
        {deletedTasks.map((task) => (
          <div key={task.id} className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-medium text-gray-900 mb-2">{task.title}</h3>
                {task.description && (
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">{task.description}</p>
                )}
                
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-4">
                  <div className="flex items-center space-x-1">
                    <User className="h-4 w-4" />
                    <span>{task.project_name}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>Created: {formatDate(task.created_at)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Clock className="h-4 w-4" />
                    <span>Deleted: {task.deleted_at ? formatDate(task.deleted_at) : 'Unknown'}</span>
                  </div>
                </div>

                {task.deletion_reason && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-2 mb-4">
                    <p className="text-sm text-red-800">
                      <span className="font-medium">Deletion reason:</span> {task.deletion_reason}
                    </p>
                  </div>
                )}

                {task.is_blocked && task.blocked_reason && (
                  <div className="bg-orange-50 border border-orange-200 rounded-md p-2 mb-4">
                    <p className="text-sm text-orange-800">
                      <span className="font-medium">Blocked:</span> {task.blocked_reason}
                    </p>
                  </div>
                )}
              </div>

              <div className="flex flex-col space-y-2 ml-4">
                <div className="text-sm font-medium text-gray-700 mb-1">Recover to:</div>
                {statusValues.map((status) => (
                  <button
                    key={status.key}
                    onClick={() => handleRecoverTask(task, status.key)}
                    disabled={recovering === task.id}
                    className="flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-md border transition-colors disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                    style={{
                      borderColor: status.color,
                      color: status.color,
                    }}
                  >
                    <RotateCcw className="h-4 w-4" />
                    <span>{status.label}</span>
                    {recovering === task.id && (
                      <div className="animate-spin rounded-full h-3 w-3 border border-current border-t-transparent"></div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
