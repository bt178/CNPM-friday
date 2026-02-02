import axios from 'axios';

const RAW_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const normalizedBaseUrl = RAW_BASE_URL.replace(/\/+$/, '');
const BASE_URL = normalizedBaseUrl.endsWith('/api/v1')
    ? normalizedBaseUrl
    : `${normalizedBaseUrl}/api/v1`;

const apiClient = axios.create({
    baseURL: BASE_URL,
});

apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default apiClient;
