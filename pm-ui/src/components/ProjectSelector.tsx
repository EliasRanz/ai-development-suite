import { useState } from 'react';
import { Project } from '../types';
import { ChevronDown, Folder } from 'lucide-react';

interface ProjectSelectorProps {
  projects: Project[];
  selectedProject: Project | null;
  onProjectChange: (project: Project) => void;
}

export default function ProjectSelector({ projects, selectedProject, onProjectChange }: ProjectSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 bg-white border border-gray-300 rounded-lg px-4 py-2 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <Folder className="w-4 h-4 text-gray-600" />
        <span className="font-medium">
          {selectedProject ? selectedProject.name : 'Select Project'}
        </span>
        <ChevronDown className="w-4 h-4 text-gray-400" />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
          <div className="p-2">
            {projects.map((project) => (
              <button
                key={project.id}
                onClick={() => {
                  onProjectChange(project);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 transition-colors ${
                  selectedProject?.id === project.id ? 'bg-blue-50 text-blue-700' : ''
                }`}
              >
                <div className="font-medium">{project.name}</div>
                {project.description && (
                  <div className="text-sm text-gray-500 truncate">{project.description}</div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
