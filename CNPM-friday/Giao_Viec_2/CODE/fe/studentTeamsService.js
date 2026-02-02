import apiClient from './apiClient';

export const studentTeamsService = {
  listTopics: () => apiClient.get('/topics'),
  createTeam: (payload) => apiClient.post('/teams', payload),
  getTeam: (teamId) => apiClient.get(`/teams/${teamId}`),
  joinTeam: (teamId, joinCode) => apiClient.post(`/teams/${teamId}/join`, null, { params: { join_code: joinCode } }),
  leaveTeam: (teamId) => apiClient.post(`/teams/${teamId}/leave`),
};
