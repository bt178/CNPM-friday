import axios from 'axios';
import { mockSubjects, mockClasses, mockUsers, mockProjects } from './mockData';

// 1. Định nghĩa Base URL
const BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
});

// 2. Thêm token vào header 
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Helper to simulate network delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// --- LocalStorage Helpers ---
const loadData = (key, defaultData) => {
  try {
    const stored = localStorage.getItem(key);
    if (stored) return JSON.parse(stored);
  } catch (e) {
    console.error(`Error parsing ${key} from localStorage`, e);
  }
  localStorage.setItem(key, JSON.stringify(defaultData));
  return [...defaultData]; // Return copy
};

const saveData = (key, data) => {
  localStorage.setItem(key, JSON.stringify(data));
};

// Initialize Data
let localUsers = loadData('users', mockUsers);
let localSubjects = loadData('subjects', mockSubjects);
let localClasses = loadData('classes', mockClasses);
let localProjects = loadData('projects', mockProjects);


// Helper for pagination & search
const mockFetch = async (data, params) => {
  await delay(500); // Simulate 500ms latency
  let result = [...data];

  // Search
  if (params?.search) {
    const s = params.search.toLowerCase();
    result = result.filter(item =>
      Object.values(item).some(val =>
        String(val).toLowerCase().includes(s)
      )
    );
  }

  // Pagination
  const skip = params?.skip || 0;
  const limit = params?.limit || 10;

  return {
    data: result.slice(skip, skip + limit),
    total: result.length
  };
};

// 3. User Service 
export const userService = {
  updateProfile: async (data) => { await delay(500); return { data: { ...localUsers[0], ...data } }; },
  changePassword: async (data) => { await delay(500); return { data: { success: true } }; },
  uploadAvatar: async (file) => { await delay(500); return { data: { url: 'https://i.pravatar.cc/150' } }; },

  // Admin only
  getAll: (params) => mockFetch(localUsers, params),
  create: async (data) => {
    await delay(500);
    if (localUsers.some(u => u.email === data.email)) {
      throw new Error('Email already exists');
    }
    const newUser = { ...data, user_id: `u${Date.now()}` };
    localUsers.push(newUser);
    saveData('users', localUsers);
    return { data: newUser };
  },
};

// 4. Subject Service 
export const subjectService = {
  getAll: (params) => mockFetch(localSubjects, params),
  create: async (data) => {
    await delay(500);
    if (localSubjects.some(s => s.subject_code === data.subject_code)) {
      throw new Error('Subject code already exists');
    }
    const newSubject = { ...data, subject_id: Date.now() };
    localSubjects.push(newSubject);
    saveData('subjects', localSubjects);
    return { data: newSubject };
  },
  update: async (id, data) => {
    await delay(500);
    const idx = localSubjects.findIndex(s => s.subject_id === id);
    if (idx > -1) {
      localSubjects[idx] = { ...localSubjects[idx], ...data };
      saveData('subjects', localSubjects);
    }
    return { data: localSubjects[idx] };
  },
  delete: async (id) => {
    await delay(500);
    const idx = localSubjects.findIndex(s => s.subject_id === id);
    if (idx > -1) {
      localSubjects.splice(idx, 1);
      saveData('subjects', localSubjects);
    }
    return { data: { success: true } };
  }
};

// 5. Class Service
export const classService = {
  getAll: (params) => mockFetch(localClasses, params),
  create: async (data) => {
    await delay(500);
    if (localClasses.some(c => c.class_code === data.class_code)) {
      throw new Error('Class code already exists');
    }
    const newClass = { ...data, class_id: Date.now() };
    localClasses.push(newClass);
    saveData('classes', localClasses);
    return { data: newClass };
  },
  update: async (id, data) => {
    await delay(500);
    const idx = localClasses.findIndex(c => c.class_id === id);
    if (idx > -1) {
      localClasses[idx] = { ...localClasses[idx], ...data };
      saveData('classes', localClasses);
    }
    return { data: localClasses[idx] };
  },
  delete: async (id) => {
    await delay(500);
    const idx = localClasses.findIndex(c => c.class_id === id);
    if (idx > -1) {
      localClasses.splice(idx, 1);
      saveData('classes', localClasses);
    }
    return { data: { success: true } };
  }
};

// 6. Project Service (For Student View)
export const projectService = {
  getAll: (params) => mockFetch(localProjects, params),
  update: async (key, data) => {
    await delay(500);
    const idx = localProjects.findIndex(p => p.key === key);
    if (idx > -1) {
      localProjects[idx] = { ...localProjects[idx], ...data };
      saveData('projects', localProjects);
    }
    return { data: localProjects[idx] };
  }
};

export default api;