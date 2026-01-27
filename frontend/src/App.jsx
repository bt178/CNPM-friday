import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProjectListView from './pages/ProjectListView';
import UserProfile from './pages/UserProfile';
import AdminDashboard from './pages/AdminDashboard';
import DashboardPage from './pages/DashboardPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import { useAuth, getDefaultDashboardPath, resolveRoleName } from './components/AuthContext';

const adminRoleGate = ['ADMIN', 'STAFF', 'HEAD_DEPT'];

const LoadingScreen = () => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
    Loading...
  </div>
);

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, isAuthReady } = useAuth();

  if (!isAuthReady) {
    return <LoadingScreen />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && allowedRoles.length) {
    const userRole = resolveRoleName(user);
    if (!userRole || !allowedRoles.includes(userRole)) {
      return <Navigate to={getDefaultDashboardPath(user)} replace />;
    }
  }

  return children;
};

const PublicRoute = ({ children }) => {
  const { user, isAuthReady } = useAuth();

  if (!isAuthReady) {
    return <LoadingScreen />;
  }

  if (user) {
    return <Navigate to={getDefaultDashboardPath(user)} replace />;
  }

  return children;
};

const LandingRedirect = () => {
  const { user, isAuthReady } = useAuth();

  if (!isAuthReady) {
    return <LoadingScreen />;
  }

  if (user) {
    return <Navigate to={getDefaultDashboardPath(user)} replace />;
  }

  return <Navigate to="/login" replace />;
};

const App = () => (
  <Routes>
    <Route path="/" element={<LandingRedirect />} />
    <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
    <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
    <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
    <Route path="/projects" element={<ProtectedRoute><ProjectListView /></ProtectedRoute>} />
    <Route path="/profile" element={<ProtectedRoute><UserProfile /></ProtectedRoute>} />
    <Route path="/admin" element={<ProtectedRoute allowedRoles={adminRoleGate}><AdminDashboard /></ProtectedRoute>} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

export default App;