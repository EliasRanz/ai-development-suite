import { Task, StatusValue, PriorityValue } from '../types';
import TaskCard from './TaskCard';

interface KanbanBoardProps {
  tasks: Task[];
  statusValues: StatusValue[];
  priorityValues: PriorityValue[];
  onEditTask: (task: Task) => void;
}

export default function KanbanBoard({ tasks, statusValues, priorityValues, onEditTask }: KanbanBoardProps) {
  const getTasksForColumn = (statusKey: string) => {
    return tasks.filter(task => task.status === statusKey);
  };

  const getPriorityConfig = (priorityKey: string) => {
    return priorityValues.find(p => p.key === priorityKey) || priorityValues[0];
  };

  return (
    <div className="flex space-x-6 overflow-x-auto pb-6">
      {statusValues.map((status) => {
        const columnTasks = getTasksForColumn(status.key);

        return (
          <div key={status.key} className="flex-shrink-0">
            <div className="kanban-column">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: status.color }}
                  ></div>
                  <h3 className="font-semibold text-gray-700">{status.label}</h3>
                </div>
                <span className="text-sm text-gray-500 bg-gray-200 rounded-full px-2 py-1">
                  {columnTasks.length}
                </span>
              </div>

              <div className="space-y-3">
                {columnTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    priorityConfig={getPriorityConfig(task.priority)}
                    onEdit={onEditTask}
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
