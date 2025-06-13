const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
const { Pool } = require('pg');
require('dotenv').config({ path: '../.env' });

const app = express();
const PORT = process.env.PORT || 8000;

// Database connection
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: process.env.AI_PM_DB_NAME || 'ai_project_manager',
  user: process.env.AI_PM_DB_USER || 'aipm',
  password: process.env.AI_PM_DB_PASSWORD || 'aipm123',
});

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Projects endpoints
app.get('/api/projects', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM projects ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching projects:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/projects', async (req, res) => {
  try {
    const { name, description } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Project name is required' });
    }
    
    const result = await pool.query(
      'INSERT INTO projects (name, description) VALUES ($1, $2) RETURNING *',
      [name, description]
    );
    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Error creating project:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/projects/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('SELECT * FROM projects WHERE id = $1', [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error fetching project:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Tasks endpoints
app.get('/api/tasks', async (req, res) => {
  try {
    const { project_id, status } = req.query;
    let query = `
      SELECT t.*, p.name as project_name 
      FROM tasks t 
      JOIN projects p ON t.project_id = p.id 
    `;
    const params = [];
    const conditions = [];

    if (project_id) {
      conditions.push(`t.project_id = $${params.length + 1}`);
      params.push(project_id);
    }

    if (status) {
      conditions.push(`t.status = $${params.length + 1}`);
      params.push(status);
    }

    if (conditions.length > 0) {
      query += 'WHERE ' + conditions.join(' AND ');
    }

    query += ' ORDER BY t.created_at DESC';

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching tasks:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/tasks', async (req, res) => {
  try {
    const { project_id, title, description, priority = 'medium' } = req.body;
    
    if (!project_id || !title) {
      return res.status(400).json({ error: 'Project ID and title are required' });
    }

    const result = await pool.query(
      'INSERT INTO tasks (project_id, title, description, priority) VALUES ($1, $2, $3, $4) RETURNING *',
      [project_id, title, description, priority]
    );
    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Error creating task:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.put('/api/tasks/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { title, description, status, priority } = req.body;
    
    const updateFields = [];
    const params = [];
    let paramCount = 1;

    if (title !== undefined) {
      updateFields.push(`title = $${paramCount++}`);
      params.push(title);
    }
    if (description !== undefined) {
      updateFields.push(`description = $${paramCount++}`);
      params.push(description);
    }
    if (status !== undefined) {
      updateFields.push(`status = $${paramCount++}`);
      params.push(status);
    }
    if (priority !== undefined) {
      updateFields.push(`priority = $${paramCount++}`);
      params.push(priority);
    }

    updateFields.push(`updated_at = CURRENT_TIMESTAMP`);
    params.push(id);

    const query = `UPDATE tasks SET ${updateFields.join(', ')} WHERE id = $${paramCount} RETURNING *`;
    const result = await pool.query(query, params);

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Task not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error updating task:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Notes endpoints
app.get('/api/notes', async (req, res) => {
  try {
    const { project_id, task_id } = req.query;
    let query = 'SELECT * FROM notes';
    const params = [];
    const conditions = [];

    if (project_id) {
      conditions.push(`project_id = $${params.length + 1}`);
      params.push(project_id);
    }

    if (task_id) {
      conditions.push(`task_id = $${params.length + 1}`);
      params.push(task_id);
    }

    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += ' ORDER BY created_at DESC';

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching notes:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/notes', async (req, res) => {
  try {
    const { project_id, task_id, content } = req.body;
    
    if (!project_id || !content) {
      return res.status(400).json({ error: 'Project ID and content are required' });
    }

    const result = await pool.query(
      'INSERT INTO notes (project_id, task_id, content) VALUES ($1, $2, $3) RETURNING *',
      [project_id, task_id || null, content]
    );
    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Error creating note:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Dashboard/Stats endpoint
app.get('/api/dashboard', async (req, res) => {
  try {
    const projectsResult = await pool.query('SELECT COUNT(*) as total FROM projects');
    const tasksResult = await pool.query(`
      SELECT 
        status,
        COUNT(*) as count
      FROM tasks 
      GROUP BY status
    `);
    const recentTasksResult = await pool.query(`
      SELECT t.*, p.name as project_name 
      FROM tasks t 
      JOIN projects p ON t.project_id = p.id 
      ORDER BY t.updated_at DESC 
      LIMIT 10
    `);

    const tasksByStatus = {};
    tasksResult.rows.forEach(row => {
      tasksByStatus[row.status] = parseInt(row.count);
    });

    res.json({
      totalProjects: parseInt(projectsResult.rows[0].total),
      tasksByStatus,
      recentTasks: recentTasksResult.rows
    });
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'API endpoint not found' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 AI Project Manager API running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  pool.end();
  process.exit(0);
});
