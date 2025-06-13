import { Task, PriorityValue } from '../types';
import { Clock, User, AlertCircle } from 'lucide-react';

interface TaskCardProps {
  task: Task;
  priorityConfig: PriorityValue;
  onEdit: (task: Task) => void;
}

export default function TaskCard({ task, priorityConfig, onEdit }: TaskCardProps) {
  // Map priority colors to Tailwind classes
  const getColorClasses = (color: string) => {
    const colorMap: Record<string, string> = {
      '#ef4444': 'border-red-200 bg-red-50 text-red-800', // red-500
      '#f97316': 'border-orange-200 bg-orange-50 text-orange-800', // orange-500
      '#eab308': 'border-yellow-200 bg-yellow-50 text-yellow-800', // yellow-500
      '#22c55e': 'border-green-200 bg-green-50 text-green-800', // green-500
      '#3b82f6': 'border-blue-200 bg-blue-50 text-blue-800', // blue-500
      '#8b5cf6': 'border-purple-200 bg-purple-50 text-purple-800', // purple-500
      '#6b7280': 'border-gray-200 bg-gray-50 text-gray-800', // gray-500
    };
    return colorMap[color] || 'border-gray-200 bg-gray-50 text-gray-800';
  };

  const priorityStyle = getColorClasses(priorityConfig.color);
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const isUrgent = priorityConfig.level >= 4;

  return (
    <div
      className={`kanban-card ${priorityStyle} cursor-pointer hover:shadow-md transition-shadow`}
      onClick={() => onEdit(task)}
    >
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-medium text-sm leading-tight flex-1 pr-2">
          {task.title}
        </h4>
        <span className="text-xs whitespace-nowrap flex items-center space-x-1">
          {priorityConfig.icon && <span>{priorityConfig.icon}</span>}
          <span>{priorityConfig.label}</span>
        </span>
      </div>

      {task.description && (
        <p className="text-gray-600 text-xs mb-3 line-clamp-3">
          {task.description}
        </p>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-1">
          <Clock className="w-3 h-3" />
          <span>{formatDate(task.created_at)}</span>
        </div>
        
        {task.project_name && (
          <div className="flex items-center space-x-1">
            <User className="w-3 h-3" />
            <span className="truncate max-w-20">{task.project_name}</span>
          </div>
        )}
      </div>

      {isUrgent && (
        <div className="absolute top-2 right-2">
          <AlertCircle className="w-4 h-4" style={{ color: priorityConfig.color }} />
        </div>
      )}
    </div>
  );
}
