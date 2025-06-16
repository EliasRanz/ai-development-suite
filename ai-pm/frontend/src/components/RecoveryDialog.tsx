import { useState } from 'react';
import { X, RotateCcw } from 'lucide-react';
import { Task } from '../types';

interface RecoveryDialogProps {
  task: Task;
  isOpen: boolean;
  onClose: () => void;
  onRecover: (taskId: number, status: string, priority?: string) => Promise<void>;
}

export default function RecoveryDialog({ task, isOpen, onClose, onRecover }: RecoveryDialogProps) {
  const [selectedStatus, setSelectedStatus] = useState<string>('todo');
  const [selectedPriority, setSelectedPriority] = useState<string>(task.priority || 'medium');
  const [isRecovering, setIsRecovering] = useState(false);

  const statusOptions: { value: string; label: string; description: string }[] = [
    { value: 'todo', label: 'To Do', description: 'Task is ready to be worked on' },
    { value: 'in-progress', label: 'In Progress', description: 'Task is currently being worked on' },
    { value: 'done', label: 'Done', description: 'Task has been completed' }
  ];

  const priorityOptions: { value: string; label: string }[] = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'urgent', label: 'Urgent' }
  ];

  const handleRecover = async () => {
    try {
      setIsRecovering(true);
      await onRecover(task.id, selectedStatus, selectedPriority);
      onClose();
    } catch (error) {
      console.error('Failed to recover task:', error);
    } finally {
      setIsRecovering(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <RotateCcw className="w-5 h-5 text-green-600" />
            <h2 className="text-lg font-semibold text-gray-900">Recover Task</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          <div className="mb-4">
            <h3 className="font-medium text-gray-900 mb-2">{task.title}</h3>
            <p className="text-sm text-gray-600 mb-4">
              Choose the state to recover this task to:
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <div className="space-y-2">
                {statusOptions.map((option) => (
                  <label key={option.value} className="flex items-start space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      name="status"
                      value={option.value}
                      checked={selectedStatus === option.value}
                      onChange={(e) => setSelectedStatus(e.target.value)}
                      className="mt-1"
                    />
                    <div>
                      <div className="text-sm font-medium text-gray-900">{option.label}</div>
                      <div className="text-xs text-gray-500">{option.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority
              </label>
              <select
                value={selectedPriority}
                onChange={(e) => setSelectedPriority(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {priorityOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={isRecovering}
          >
            Cancel
          </button>
          <button
            onClick={handleRecover}
            disabled={isRecovering}
            className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>{isRecovering ? 'Recovering...' : 'Recover Task'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
