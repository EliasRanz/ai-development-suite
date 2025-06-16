import { BrowserRouter, Routes, Route, useNavigate, useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import App from './App';
import BoardSelection from './components/BoardSelection';
import GlobalDashboard from './components/GlobalDashboard';
import GlobalDeletedView from './components/GlobalDeletedView';
import Layout from './components/Layout';
import { Project } from './types';
import { api } from './api';

function AppContent() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);

  // Load projects on mount
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const projectsData = await api.getProjects();
        setProjects(projectsData);
      } catch (err) {
        console.error('Failed to load projects:', err);
      }
    };

    loadProjects();
  }, []);

  const handleBoardSelection = () => {
    navigate('/projects');
  };

  const handleHomeClick = () => {
    navigate('/');
  };

  const handleProjectSelect = (project: Project) => {
    const slug = project.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    navigate(`/projects/${slug}`);
  };

  const handleGlobalViewChange = (view: 'kanban' | 'dashboard' | 'deleted') => {
    if (view === 'kanban') {
      navigate('/projects');
    } else {
      navigate(`/${view}`);
    }
  };

  return (
    <Routes>
      <Route 
        path="/" 
        element={
          <Layout 
            currentView="kanban"
            onViewChange={handleGlobalViewChange}
            onBoardSelection={handleBoardSelection}
            onHomeClick={handleHomeClick}
            projects={projects}
            onProjectSelect={handleProjectSelect}
          >
            <BoardSelection onProjectSelect={handleProjectSelect} />
          </Layout>
        } 
      />
      <Route 
        path="/projects" 
        element={
          <Layout 
            currentView="kanban"
            onViewChange={handleGlobalViewChange}
            onBoardSelection={handleBoardSelection}
            onHomeClick={handleHomeClick}
            projects={projects}
            onProjectSelect={handleProjectSelect}
          >
            <BoardSelection onProjectSelect={handleProjectSelect} />
          </Layout>
        } 
      />
      <Route 
        path="/dashboard" 
        element={
          <Layout 
            currentView="dashboard"
            onViewChange={handleGlobalViewChange}
            onBoardSelection={handleBoardSelection}
            onHomeClick={handleHomeClick}
            projects={projects}
            onProjectSelect={handleProjectSelect}
          >
            <GlobalDashboard />
          </Layout>
        } 
      />
      <Route 
        path="/deleted" 
        element={
          <Layout 
            currentView="deleted"
            onViewChange={handleGlobalViewChange}
            onBoardSelection={handleBoardSelection}
            onHomeClick={handleHomeClick}
            projects={projects}
            onProjectSelect={handleProjectSelect}
          >
            <GlobalDeletedView projects={projects} />
          </Layout>
        } 
      />
      <Route 
        path="/projects/:projectSlug" 
        element={
          <ProjectWrapper 
            onBoardSelection={handleBoardSelection} 
            onHomeClick={handleHomeClick}
            globalProjects={projects}
            onProjectSelect={handleProjectSelect}
          />
        } 
      />
      <Route 
        path="/projects/:projectSlug/:view" 
        element={
          <ProjectWrapper 
            onBoardSelection={handleBoardSelection} 
            onHomeClick={handleHomeClick}
            globalProjects={projects}
            onProjectSelect={handleProjectSelect}
          />
        } 
      />
      <Route 
        path="/projects/:projectSlug/tasks/:taskId" 
        element={
          <ProjectWrapper 
            onBoardSelection={handleBoardSelection} 
            onHomeClick={handleHomeClick}
            globalProjects={projects}
            onProjectSelect={handleProjectSelect}
          />
        } 
      />
    </Routes>
  );
}

// Simple wrapper that gets current view from URL and passes navigation handlers
function ProjectWrapper({ 
  onBoardSelection, 
  onHomeClick,
  globalProjects = [], 
  onProjectSelect 
}: { 
  onBoardSelection: () => void;
  onHomeClick?: () => void;
  globalProjects?: Project[];
  onProjectSelect?: (project: Project) => void;
}) {
  const { view, projectSlug } = useParams();
  const navigate = useNavigate();
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  
  const currentView = (view as 'kanban' | 'dashboard' | 'deleted') || 'kanban';

  // Utility function to create URL-friendly slug from project name
  const createProjectSlug = (project: Project): string => {
    return project.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  // Utility function to find project by slug or ID
  const findProjectBySlug = (slug: string): Project | null => {
    if (!globalProjects.length) return null;
    
    // First try to find by slug (converted from name)
    const projectBySlug = globalProjects.find(p => createProjectSlug(p) === slug);
    if (projectBySlug) return projectBySlug;
    
    // Fallback to finding by ID if slug is numeric
    const projectId = parseInt(slug);
    if (!isNaN(projectId)) {
      return globalProjects.find(p => p.id === projectId) || null;
    }
    
    return null;
  };

  // Resolve project from URL slug
  useEffect(() => {
    if (projectSlug && globalProjects.length > 0) {
      const project = findProjectBySlug(projectSlug);
      if (project && (!selectedProject || selectedProject.id !== project.id)) {
        setSelectedProject(project);
      } else if (!project) {
        // Project not found, redirect to projects list
        navigate('/projects', { replace: true });
      }
    }
  }, [projectSlug, globalProjects, selectedProject, navigate]);

  const handleViewChange = (newView: 'kanban' | 'dashboard' | 'deleted') => {
    if (newView === 'deleted') {
      // Always navigate to global deleted view
      navigate('/deleted');
    } else if (projectSlug) {
      navigate(`/projects/${projectSlug}/${newView}`);
    }
  };

  return (
    <Layout 
      currentView={currentView}
      onViewChange={handleViewChange}
      onBoardSelection={onBoardSelection}
      onHomeClick={onHomeClick}
      selectedProject={selectedProject}
      showProjectViews={true}
      projects={globalProjects}
      onProjectSelect={onProjectSelect}
    >
      <App selectedProject={selectedProject} />
    </Layout>
  );
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
