package domain

// ProjectRepository defines the interface for project data operations
type ProjectRepository interface {
	// Project operations
	CreateProject(project *Project) error
	GetProject(id int) (*Project, error)
	GetAllProjects() ([]*Project, error)
	UpdateProject(project *Project) error
	DeleteProject(id int) error

	// Task operations
	CreateTask(task *Task) error
	GetTask(id int) (*Task, error)
	GetTasksByProject(projectID int) ([]*Task, error)
	GetAllTasks() ([]*Task, error)
	UpdateTask(task *Task) error
	DeleteTask(id int) error

	// Note operations
	CreateNote(note *Note) error
	GetNotesByProject(projectID int) ([]*Note, error)
	GetNotesByTask(taskID int) ([]*Note, error)
	DeleteNote(id int) error
}

// ProjectService defines the business logic interface
type ProjectService interface {
	// Project management
	CreateProject(name, description string) (*Project, error)
	GetProject(id int) (*Project, error)
	GetAllProjects() ([]*Project, error)
	UpdateProjectStatus(id int, status string) error

	// Task management
	CreateTask(projectID int, title, description, priority string) (*Task, error)
	GetTask(id int) (*Task, error)
	GetTasksByProject(projectID int) ([]*Task, error)
	GetAllTasks() ([]*Task, error)
	UpdateTaskStatus(id int, status string) error
	UpdateTaskPriority(id int, priority string) error

	// Note management
	AddNote(projectID int, taskID *int, content string) (*Note, error)
	GetProjectNotes(projectID int) ([]*Note, error)
	GetTaskNotes(taskID int) ([]*Note, error)

	// Statistics and reporting
	GetProjectStats(projectID int) (*ProjectStats, error)
	GetOverallStats() (*OverallStats, error)
}

// ProjectStats represents statistics for a specific project
type ProjectStats struct {
	ProjectID     int `json:"project_id"`
	TotalTasks    int `json:"total_tasks"`
	CompletedTasks int `json:"completed_tasks"`
	InProgressTasks int `json:"in_progress_tasks"`
	TodoTasks     int `json:"todo_tasks"`
	ReviewTasks   int `json:"review_tasks"`
	HighPriorityTasks int `json:"high_priority_tasks"`
	UrgentTasks   int `json:"urgent_tasks"`
}

// OverallStats represents overall system statistics
type OverallStats struct {
	TotalProjects   int `json:"total_projects"`
	ActiveProjects  int `json:"active_projects"`
	TotalTasks      int `json:"total_tasks"`
	CompletedTasks  int `json:"completed_tasks"`
	InProgressTasks int `json:"in_progress_tasks"`
	OverdueTasks    int `json:"overdue_tasks"`
}
