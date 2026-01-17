import axiosInstance from './api';

// Đăng nhập
export const login = async (email, password) => {
    // FastAPI dùng OAuth2PasswordRequestForm nên cần truyền dạng form-urlencoded
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    return axiosInstance.post('/api/v1/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
};

// Đăng ký
export const register = async (data) => {
    // data: { email, password, role_id, full_name }
    return axiosInstance.post('/api/v1/auth/register', data);
};
