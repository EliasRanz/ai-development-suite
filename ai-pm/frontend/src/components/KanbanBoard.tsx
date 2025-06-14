import { Task, StatusValue, PriorityValue } from '../types';
import TaskCard from './TaskCard';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';

interface KanbanBoardProps {
  tasks: Task[];
  statusValues: StatusValue[];
  priorityValues: PriorityValue[];
  onViewTask?: (task: Task) => void;
}

export default function KanbanBoard({ tasks, statusValues, priorityValues, onViewTask }: KanbanBoardProps) {
  const [collapsedColumns, setCollapsedColumns] = useState<Set<string>>(
    new Set(['done', 'deleted']) // Default: collapse completed and deleted columns
  );

  const toggleColumn = (statusKey: string) => {
    const newCollapsed = new Set(collapsedColumns);
    if (newCollapsed.has(statusKey)) {
      newCollapsed.delete(statusKey);
    } else {
      newCollapsed.add(statusKey);
    }
    setCollapsedColumns(newCollapsed);
  };
  const getTasksForColumn = (statusKey: string) => {
    return tasks.filter(task => task.status === statusKey);
  };

  const getPriorityConfig = (priorityKey: string) => {
    return priorityValues.find(p => p.key === priorityKey) || priorityValues[0];
  };  return (
    <div className="flex space-x-3 sm:space-x-4 lg:space-x-6 overflow-x-auto pb-6 relative px-2 sm:px-4 lg:px-6">
      {statusValues.map((status) => {
        const columnTasks = getTasksForColumn(status.key);
        const isCollapsed = collapsedColumns.has(status.key);

        if (isCollapsed) {
          // Render collapsed column as a completely separate, isolated component
          return (
            <div key={status.key} className="flex-shrink-0 w-12 sm:w-14 lg:w-16">
              <div className="w-12 sm:w-14 lg:w-16 bg-gray-50 rounded-lg border border-gray-200 min-h-[500px] max-h-[500px] overflow-hidden transition-all duration-300 relative">
                <div className="flex flex-col items-center p-2 h-full relative">
                  <button
                    onClick={() => toggleColumn(status.key)}
                    className="p-1 hover:bg-gray-200 rounded transition-colors mb-3"
                    title={`Expand ${status.label}`}
                  >
                    <ChevronRight className="w-4 h-4 text-gray-600" />
                  </button>
                  <div 
                    className="w-4 h-4 rounded-full shadow-sm mb-3"
                    style={{ backgroundColor: status.color }}
                    title={status.label}
                  ></div>
                  <div className="bg-white rounded-full px-2 py-1 text-xs font-medium text-gray-700 shadow-sm border">
                    {columnTasks.length}
                  </div>
                  {/* Vertical text positioned with consistent spacing from count */}
                  <div className="mt-8">
                    <div 
                      className="text-xs font-medium text-gray-600 transform -rotate-90 whitespace-nowrap"
                      style={{ transformOrigin: 'center' }}
                    >
                      {status.label}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        }

        // Render expanded column
        return (
          <div key={status.key} className="flex-shrink-0">
            <div className="kanban-column transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleColumn(status.key)}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                    title={`Collapse ${status.label}`}
                  >
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                  </button>
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: status.color }}
                  ></div>
                  <h3 className="font-semibold text-gray-700">{status.label}</h3>
                </div>
                <span className="text-sm text-gray-500 bg-gray-200 rounded-full px-2 py-1 font-medium">
                  {columnTasks.length}
                </span>
              </div>

              <div className="space-y-3">
                {columnTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    priorityConfig={getPriorityConfig(task.priority)}
                    isBlocked={task.is_blocked}
                    onView={onViewTask}
                  />
                ))}

                {columnTasks.length === 0 && (
                  <div className="text-center py-8 text-gray-400">
                    <p className="text-sm">No tasks</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
