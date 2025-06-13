import React from 'react';
import { Feature } from '../types';
import TaskCard from './TaskCard';
import { Folder, ChevronDown, ChevronRight } from 'lucide-react';

interface FeatureGroupProps {
  feature: Feature;
  onEditTask: (task: any) => void;
}

export default function FeatureGroup({ feature, onEditTask }: FeatureGroupProps) {
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  return (
    <div className="mb-4 border rounded-lg overflow-hidden" style={{ borderColor: feature.color }}>
      <div
        className="px-3 py-2 cursor-pointer flex items-center justify-between"
        style={{ backgroundColor: feature.color + '20' }}
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <div className="flex items-center space-x-2">
          <Folder className="w-4 h-4" style={{ color: feature.color }} />
          <span className="font-medium text-sm">{feature.name}</span>
          <span className="text-xs text-gray-500 bg-white rounded-full px-2 py-1">
            {feature.tasks.length}
          </span>
        </div>
        
        {isCollapsed ? (
          <ChevronRight className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </div>

      {!isCollapsed && (
        <div className="p-2 bg-gray-50">
          {feature.tasks.map((task, index) => (
            <div key={task.id} className="mb-2 last:mb-0">
              <TaskCard
                task={task}
                index={index}
                onEdit={onEditTask}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
