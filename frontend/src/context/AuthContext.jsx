import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = authService.getToken();
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const userData = await authService.getMe();
        setUser(userData);
      } catch (err) {
        console.warn('Session expired or invalid token:', err.message);
        authService.logout();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = async (username, password) => {
    await authService.login(username, password);
    const userData = await authService.getMe();
    setUser(userData);
    return userData;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const hasPermission = (permissionCode) => {
    if (!user || !user.permissions) return false;
    return Boolean(user.permissions[permissionCode]);
  };

  const getConstraint = (permissionCode, constraintKey) => {
    if (!user || !user.permissions) return null;
    return user.permissions[permissionCode]?.[constraintKey] ?? null;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: Boolean(user),
        isLoading,
        login,
        logout,
        hasPermission,
        getConstraint,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
