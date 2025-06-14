import { Project, Task, DashboardData, CreateProjectRequest, CreateTaskRequest, UpdateTaskRequest, StatusValue, PriorityValue, Note } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchWithError(url: string, options?: RequestInit): Promise<Response> {
  const response = await fetch(url, options);
  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText || `HTTP ${response.status}`);
  }
  return response;
}

export const api = {
  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetchWithError(`${API_BASE_URL}/health`);
    return response.json();
  },

  // Dashboard
  async getDashboard(): Promise<DashboardData> {
    const response = await fetchWithError(`${API_BASE_URL}/dashboard`);
    return response.json();
  },

  // Projects
  async getProjects(): Promise<Project[]> {
    const response = await fetchWithError(`${API_BASE_URL}/projects`);
    return response.json();
  },

  async createProject(project: CreateProjectRequest): Promise<Project> {
    const response = await fetchWithError(`${API_BASE_URL}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(project),
    });
    return response.json();
  },

  // Tasks
  async getTasks(projectId?: number, status?: string): Promise<Task[]> {
    const params = new URLSearchParams();
    if (projectId) params.append('project_id', projectId.toString());
    if (status) params.append('status', status);
    
    const response = await fetchWithError(`${API_BASE_URL}/tasks?${params}`);
    return response.json();
  },

  async createTask(task: CreateTaskRequest): Promise<Task> {
    const response = await fetchWithError(`${API_BASE_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    });
    return response.json();
  },

  async updateTask(id: number, updates: UpdateTaskRequest): Promise<Task> {
    const response = await fetchWithError(`${API_BASE_URL}/tasks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return response.json();
  },

  async deleteTask(id: number, reason?: string): Promise<void> {
    await fetchWithError(`${API_BASE_URL}/tasks/${id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason: reason || 'Deleted via UI' }),
    });
  },

  async updateTaskStatus(id: number, status: string): Promise<Task> {
    return this.updateTask(id, { status });
  },

  // Status and Priority values
  async getStatusValues(): Promise<StatusValue[]> {
    const response = await fetchWithError(`${API_BASE_URL}/status-values`);
    return response.json();
  },

  async getPriorityValues(): Promise<PriorityValue[]> {
    const response = await fetchWithError(`${API_BASE_URL}/priority-values`);
    return response.json();
  },

  // Notes
  async getTaskNotes(taskId: number): Promise<Note[]> {
    const response = await fetchWithError(`${API_BASE_URL}/notes?task_id=${taskId}`);
    return response.json();
  },

  async createNote(taskId: number, content: string): Promise<Note> {
    const response = await fetchWithError(`${API_BASE_URL}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_id: taskId, content }),
    });
    return response.json();
  },

  async deleteNote(noteId: number): Promise<void> {
    await fetchWithError(`${API_BASE_URL}/notes/${noteId}`, {
      method: 'DELETE',
    });
  },

  // Task blocking
  async blockTask(taskId: number, reason: string): Promise<Task> {
    const response = await fetchWithError(`${API_BASE_URL}/tasks/${taskId}/block`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason }),
    });
    return response.json();
  },

  async unblockTask(taskId: number): Promise<Task> {
    const response = await fetchWithError(`${API_BASE_URL}/tasks/${taskId}/unblock`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return response.json();
  },

  // Deleted tasks management
  async getDeletedTasks(projectId?: number): Promise<Task[]> {
    const params = new URLSearchParams();
    if (projectId) params.append('project_id', projectId.toString());
    
    const response = await fetchWithError(`${API_BASE_URL}/tasks/deleted?${params}`);
    return response.json();
  },

  async recoverTask(taskId: number, status: string = 'todo'): Promise<Task> {
    const response = await fetchWithError(`${API_BASE_URL}/tasks/${taskId}/recover`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    return response.json();
  },
};
