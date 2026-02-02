import apiClient from './apiClient';

export const tasksService = {
  createSprint: (payload) => apiClient.post('/sprints', payload),
  getSprint: (sprintId) => apiClient.get(`/sprints/${sprintId}`),
  createTask: (payload) => apiClient.post('/tasks', payload),
  listTasks: (params) => apiClient.get('/tasks', { params }),
  updateTask: (taskId, payload) => apiClient.put(`/tasks/${taskId}`, payload),
  deleteTask: (taskId) => apiClient.delete(`/tasks/${taskId}`),
};
