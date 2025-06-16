import { useState, useEffect, useRef } from 'react';
import { Project } from '../types';
import { BarChart3, Layout, Trash2, ChevronDown, Home } from 'lucide-react';

interface HeaderProps {
  currentView: 'kanban' | 'dashboard' | 'deleted';
  onViewChange: (view: 'kanban' | 'dashboard' | 'deleted') => void;
  onBoardSelection?: () => void;
  onHomeClick?: () => void; // Navigate to home/landing page
  selectedProject: Project | null;
  showProjectViews?: boolean;
  projects?: Project[]; // List of all available projects
  onProjectSelect?: (project: Project) => void; // Callback when a project is selected
}

export default function Header({ 
  currentView, 
  onViewChange, 
  onBoardSelection, 
  onHomeClick,
  selectedProject, 
  showProjectViews = false,
  projects = [],
  onProjectSelect
}: HeaderProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isDropdownOpen]);

  const handleProjectSelect = (project: Project) => {
    setIsDropdownOpen(false);
    if (onProjectSelect) {
      onProjectSelect(project);
    }
  };

  const handleProjectsClick = () => {
    if (projects.length === 0) {
      // If no projects available, act as board selection
      if (onBoardSelection && showProjectViews) {
        onBoardSelection();
      }
    } else {
      // Toggle dropdown
      setIsDropdownOpen(!isDropdownOpen);
    }
  };
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
            {/* Home button - always visible */}
            <button
              onClick={onHomeClick}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                !showProjectViews && currentView === 'kanban'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Home className="w-4 h-4" />
              <span>Home</span>
            </button>

            {/* Projects dropdown button - always visible */}
            <div className="relative">
              <button
                onClick={handleProjectsClick}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                  showProjectViews && currentView === 'kanban'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Layout className="w-4 h-4" />
                <span>Projects</span>
                {projects.length > 0 && (
                  <ChevronDown className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
                )}
              </button>

              {/* Dropdown menu */}
              {isDropdownOpen && projects.length > 0 && (
                <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                  <div className="py-1">
                    {projects.map((project) => (
                      <button
                        key={project.id}
                        onClick={() => handleProjectSelect(project)}
                        className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors ${
                          selectedProject?.id === project.id 
                            ? 'bg-blue-50 text-blue-700 font-medium' 
                            : 'text-gray-700'
                        }`}
                      >
                        <div className="flex items-center space-x-2">
                          <Layout className="w-4 h-4" />
                          <span>{project.name}</span>
                        </div>
                        {project.description && (
                          <div className="text-xs text-gray-500 mt-1 ml-6">
                            {project.description}
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Dashboard and Deleted views - always visible */}
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
