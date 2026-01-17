import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1'; // Điều chỉnh theo route của bạn

// Tự động đính kèm Token vào mỗi request nếu có
const getHeader = () => {
  const token = localStorage.getItem('token');
  return { headers: { Authorization: `Bearer ${token}` } };
};

export const userService = {
  // Lấy thông tin user hiện tại
  getProfile: () => axios.get(`${API_URL}/users/me`, getHeader()),

  // Cập nhật thông tin (Name, Phone)
  updateProfile: (data) => axios.patch(`${API_URL}/users/me`, data, getHeader()),

  // Đổi mật khẩu
  changePassword: (data) => axios.post(`${API_URL}/users/change-password`, data, getHeader()),
};
