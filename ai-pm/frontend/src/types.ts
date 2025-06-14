export interface Project {
  id: number;
  name: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  project_id: number;
  project_name?: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  is_blocked: boolean;
  blocked_reason?: string | null;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
  deletion_reason?: string | null;
}

export interface Note {
  id: number;
  project_id: number;
  task_id?: number | null;
  content: string;
  created_at: string;
}

export interface DashboardData {
  total_projects: number;
  tasks_by_status: Record<string, number>;
  recent_tasks: Task[];
}

export interface CreateProjectRequest {
  name: string;
  description: string;
}

export interface CreateTaskRequest {
  project_id: number;
  title: string;
  description: string;
  status?: string;
  priority?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: string;
  priority?: string;
}

export interface StatusValue {
  id: number;
  key: string;
  label: string;
  description: string;
  color: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
}

export interface PriorityValue {
  id: number;
  key: string;
  label: string;
  description: string;
  color: string;
  icon: string;
  level: number;
  is_active: boolean;
  created_at: string;
}

export interface Feature {
  id: string;
  name: string;
  description: string;
  tasks: Task[];
  color: string;
}
