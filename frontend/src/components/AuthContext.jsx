import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axiosInstance from '../services/api';

const STORAGE_KEYS = {
    token: 'access_token',
    user: 'user',
};

const AuthContext = createContext();

const canUseStorage = () => typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';

const parseUser = (value) => {
    if (!value) return null;
    try {
        return JSON.parse(value);
    } catch (_err) {
        return null;
    }
};

const readStoredSession = () => {
    if (!canUseStorage()) {
        return { token: null, user: null };
    }
    const storedToken = window.localStorage.getItem(STORAGE_KEYS.token);
    const storedUserRaw = window.localStorage.getItem(STORAGE_KEYS.user);
    const storedUser = parseUser(storedUserRaw);
    if (!storedUser && storedUserRaw) {
        window.localStorage.removeItem(STORAGE_KEYS.user);
    }
    return { token: storedToken, user: storedUser };
};

const persistSession = (nextToken, nextUser) => {
    if (!canUseStorage()) {
        return;
    }
    if (nextToken) {
        window.localStorage.setItem(STORAGE_KEYS.token, nextToken);
    } else {
        window.localStorage.removeItem(STORAGE_KEYS.token);
    }

    if (nextUser) {
        window.localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(nextUser));
    } else {
        window.localStorage.removeItem(STORAGE_KEYS.user);
    }
};

export const AuthProvider = ({ children }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isAuthReady, setIsAuthReady] = useState(false);

    const clearError = useCallback(() => setError(null), []);

    useEffect(() => {
        const storedSession = readStoredSession();
        if (storedSession.token) {
            setToken(storedSession.token);
        }
        if (storedSession.user) {
            setUser(storedSession.user);
        }
        setIsAuthReady(true);
    }, []);

    useEffect(() => {
        if (!isAuthReady) {
            return;
        }
        persistSession(token, user);
    }, [token, user, isAuthReady]);

    useEffect(() => {
        if (!canUseStorage()) {
            return undefined;
        }
        const handleStorage = (event) => {
            if (event.key === STORAGE_KEYS.token) {
                setToken(event.newValue);
            }
            if (event.key === STORAGE_KEYS.user) {
                setUser(parseUser(event.newValue));
            }
        };

        window.addEventListener('storage', handleStorage);
        return () => window.removeEventListener('storage', handleStorage);
    }, []);

    useEffect(() => {
        clearError();
    }, [location.pathname, clearError]);

    const login = async (email, password) => {
        setLoading(true);
        clearError();
        try {
            const params = new URLSearchParams();
            params.append('username', email);
            params.append('password', password);
            params.append('grant_type', 'password');
            const res = await axiosInstance.post('/api/v1/auth/login', params, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            });

            const accessToken = res.data.access_token;
            setToken(accessToken);
            persistSession(accessToken, null);

            const profileRes = await axiosInstance.get('/api/v1/users/me', {
                headers: { Authorization: `Bearer ${accessToken}` },
            });

            const sessionUser = profileRes.data;
            setUser(sessionUser);
            persistSession(accessToken, sessionUser);

            navigate('/dashboard', { replace: true });
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    const register = async (registerData) => {
        setLoading(true);
        clearError();
        try {
            const res = await axiosInstance.post('/api/v1/auth/register', registerData);
            setUser(res.data);
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        persistSession(null, null);
        setToken(null);
        setUser(null);
        clearError();
        navigate('/login', { replace: true });
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, error, login, register, logout, isAuthReady, clearError }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
