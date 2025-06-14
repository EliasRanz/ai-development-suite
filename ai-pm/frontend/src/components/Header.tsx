import { Project } from '../types';
import { BarChart3, Layout, Trash2 } from 'lucide-react';

interface HeaderProps {
  currentView: 'kanban' | 'dashboard' | 'deleted';
  onViewChange: (view: 'kanban' | 'dashboard' | 'deleted') => void;
  selectedProject: Project | null;
}

export default function Header({ currentView, onViewChange, selectedProject }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Project Manager</h1>
          {selectedProject && (
            <p className="text-sm text-gray-600 mt-1">
              Project: {selectedProject.name}
            </p>
          )}
        </div>
        
        <div className="flex items-center space-x-4">          
          <nav className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => onViewChange('kanban')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                currentView === 'kanban'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Layout className="w-4 h-4" />
              <span>Kanban</span>
            </button>
            <button
              onClick={() => onViewChange('dashboard')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                currentView === 'dashboard'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Dashboard</span>
            </button>
            <button
              onClick={() => onViewChange('deleted')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                currentView === 'deleted'
                  ? 'bg-white text-red-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Trash2 className="w-4 h-4" />
              <span>Deleted</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}
