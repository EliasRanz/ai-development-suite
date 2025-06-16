import React from 'react';
import Header from './Header';
import { Project } from '../types';

interface LayoutProps {
  children: React.ReactNode;
  currentView?: 'kanban' | 'dashboard' | 'deleted';
  selectedProject?: Project | null;
  onViewChange?: (view: 'kanban' | 'dashboard' | 'deleted') => void;
  onBoardSelection?: () => void;
  onHomeClick?: () => void; // Navigate to home/landing page
  showProjectViews?: boolean; // New prop
  projects?: Project[]; // List of all available projects
  onProjectSelect?: (project: Project) => void; // Callback when a project is selected
}

export default function Layout({ 
  children, 
  currentView = 'kanban', 
  selectedProject = null,
  onViewChange = () => {},
  onBoardSelection = () => {},
  onHomeClick,
  showProjectViews = false,
  projects = [],
  onProjectSelect
}: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        currentView={currentView}
        selectedProject={selectedProject}
        onViewChange={onViewChange}
        onBoardSelection={onBoardSelection}
        onHomeClick={onHomeClick}
        showProjectViews={showProjectViews}
        projects={projects}
        onProjectSelect={onProjectSelect}
      />
      <main className="p-6">
        {children}
      </main>
    </div>
  );
}
