import React, { createContext, useState, useEffect } from 'react';
import API from '../api/axios';

// Create the Auth context
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is already logged in on component mount
  useEffect(() => {
    const checkLoggedIn = async () => {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (token) {
        try {
          const response = await API.get('/auth/me');
          setCurrentUser(response.data);
        } catch (err) {
          // If token is invalid or expired, clear local storage
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          setError('Session expired. Please login again.');
          setCurrentUser(null);
        }
      }
      
      setLoading(false);
    };

    checkLoggedIn();
  }, []);

  // Login function
  const login = async (email, password) => {
    try {
      const response = await API.post('/auth/login', { email, password });
      const { user, access_token, refresh_token } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      setCurrentUser(user);
      setError(null);
      return user;
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed. Please try again.');
      throw err;
    }
  };

  // Register function
  const register = async (username, email, password) => {
    try {
      const response = await API.post('/auth/register', { username, email, password });
      return response.data;
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed. Please try again.');
      throw err;
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    setCurrentUser(null);
  };

  // Refresh token function
  const refreshToken = async () => {
    try {
      const refresh = localStorage.getItem('refreshToken');
      if (!refresh) throw new Error('No refresh token available');
      
      const response = await API.post('/auth/refresh', {}, {
        headers: { Authorization: `Bearer ${refresh}` }
      });
      
      localStorage.setItem('token', response.data.access_token);
      return response.data.access_token;
    } catch (err) {
      logout();
      throw err;
    }
  };

  // Context value
  const value = {
    currentUser,
    loading,
    error,
    login,
    register,
    logout,
    refreshToken,
    setError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 