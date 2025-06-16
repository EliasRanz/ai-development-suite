import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Project } from '../types';
import { api } from '../api';
import LoadingSpinner from './LoadingSpinner';
import { Layout, Users, Calendar } from 'lucide-react';

interface BoardSelectionProps {
  onProjectSelect?: (project: Project) => void;
}

export default function BoardSelection({ onProjectSelect }: BoardSelectionProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Utility function to create URL-friendly slug from project name
  const createProjectSlug = (project: Project): string => {
    return project.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  useEffect(() => {
    const loadProjects = async () => {
      try {
        setLoading(true);
        const projectsData = await api.getProjects();
        setProjects(projectsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load projects');
      } finally {
        setLoading(false);
      }
    };

    loadProjects();
  }, []);

  const handleProjectSelect = (project: Project) => {
    if (onProjectSelect) {
      onProjectSelect(project);
    } else {
      const slug = createProjectSlug(project);
      navigate(`/projects/${slug}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-lg font-medium mb-2">Error Loading Projects</div>
          <div className="text-gray-600">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <>
      {projects.length === 0 ? (
        <div className="text-center py-12">
          <Layout className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Projects Found</h3>
          <p className="text-gray-600">
            It looks like there are no projects set up yet. Contact your administrator to create projects.
          </p>
        </div>
      ) : (
        <div>
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Your Projects</h2>
            <p className="text-gray-600">Choose a project to view its board</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => handleProjectSelect(project)}
                className="bg-white rounded-lg border border-gray-200 p-6 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="p-2 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                    <Layout className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                  {project.name}
                </h3>
                
                {project.description && (
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {project.description}
                  </p>
                )}
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-1">
                      <Users className="w-4 h-4" />
                      <span>ID: {project.id}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>
                      {new Date(project.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
