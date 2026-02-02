import axios from 'axios';

// 1. Define Base URL
// For local development with Docker: http://localhost:8000/api/v1
const BASE_URL = 'http://127.0.0.1:8000/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
});

// Debug: Log BASE_URL
console.log('[API] Initialized with baseURL:', BASE_URL);

// 2. Add token to header
api.interceptors.request.use((config) => {
  // User requested checking token key. logic in AuthContext uses 'access_token'.
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  console.log('[API] Request:', config.method?.toUpperCase(), config.baseURL + config.url);
  return config;
});

// --- API Services ---

// User Service
export const userService = {
  // Use for Dashboard
  getMe: async () => {
    return api.get('/users/me');
  },
  // Keep existing methods if needed by other parts, or assume they are replaced by profileService
  // For now, mapping what was requested.
};

// Profile Service
export const profileService = {
  getMe: async () => {
    return api.get('/profile/me');
  },
  updateMe: async (data) => {
    return api.put('/profile/me', data);
  }
};

// Project Service
export const projectService = {
  getAll: async (params) => {
    // params might be search/filter
    return api.get('/projects', { params });
  },
  claim: async (projectId) => {
    return api.patch(`/projects/${projectId}/claim`);
  }
};

// Team Service
export const teamService = {
  getAll: async () => {
    return api.get('/teams');
  },
  create: async (data) => {
    return api.post('/teams', data);
  },
  getDetail: async (teamId) => {
    return api.get(`/teams/${teamId}`);
  },
  join: async (teamId, data) => {
    // data might contain password if required
    return api.post(`/teams/${teamId}/join`, data);
  },
  joinByCode: async (code) => {
    return api.post('/teams/join', { join_code: code });
  },
  leave: async (teamId) => {
    return api.post(`/teams/${teamId}/leave`);
  },
  finalize: async (teamId) => {
    return api.patch(`/teams/${teamId}/finalize`);
  },
  selectProject: async (teamId, projectId) => {
    return api.patch(`/teams/${teamId}/select-project`, { project_id: projectId });
  }
};

// Task Service (Kanban)
export const taskService = {
  // Sprints
  createSprint: async (data) => {
    return api.post('/tasks/sprints', data);
  },
  getSprint: async (sprintId) => {
    return api.get(`/tasks/sprints/${sprintId}`);
  },
  getSprintTasks: async (sprintId) => {
    return api.get(`/tasks/sprints/${sprintId}/tasks`);
  },

  // Tasks
  getAllTasks: async (params) => {
    return api.get('/tasks', { params });
  },
  createTask: async (data) => {
    return api.post('/tasks', data);
  },
  getTask: async (taskId) => {
    return api.get(`/tasks/${taskId}`);
  },
  updateTask: async (taskId, data) => {
    return api.put(`/tasks/${taskId}`, data);
  },
  deleteTask: async (taskId) => {
    return api.delete(`/tasks/${taskId}`);
  },
  changeStatus: async (taskId, status) => {
    return api.patch(`/tasks/${taskId}/status`, { status });
  },
  assign: async (taskId, userId) => {
    return api.patch(`/tasks/${taskId}/assign`, { assignee_id: userId });
  }
};

export const subjectService = {
  getAll: async () => api.get('/subjects'),
  create: async (data) => api.post('/subjects', data),
  update: async (id, data) => api.put(`/subjects/${id}`, data),
  delete: async (id) => api.delete(`/subjects/${id}`)
};

export const classService = {
  getAll: async () => api.get('/classes'),
  create: async (data) => api.post('/classes', data),
  update: async (id, data) => api.put(`/classes/${id}`, data),
  delete: async (id) => api.delete(`/classes/${id}`)
};

export const semesterService = {
  getAll: async () => api.get('/semesters'),
  create: async (data) => api.post('/semesters', data),
  delete: async (id) => api.delete(`/semesters/${id}`)


};

// Export default api instance just in case
export default api;