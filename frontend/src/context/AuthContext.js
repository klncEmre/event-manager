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
          const response = await API.get('/api/auth/me/');
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

  // Load current user info if token exists
  const loadUser = async () => {
    try {
      if (localStorage.getItem('token')) {
        const response = await API.get('/api/auth/me/');
        setCurrentUser(response.data);
      }
    } catch (error) {
      // Token is invalid, clear everything
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Login
  const login = async (email, password) => {
    try {
      const response = await API.post('/api/auth/login/', { email, password });
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('refreshToken', response.data.refresh_token);
      
      // Get user info
      const userResponse = await API.get('/api/auth/me/');
      setCurrentUser(userResponse.data);
      return true;
    } catch (error) {
      throw error;
    }
  };

  // Register
  const register = async (username, email, password) => {
    try {
      const response = await API.post('/api/auth/register/', { username, email, password });
      return true;
    } catch (error) {
      throw error;
    }
  };

  // Logout
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    setCurrentUser(null);
  };

  // Refresh token
  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await API.post('/api/auth/refresh/', {}, {
        headers: {
          Authorization: `Bearer ${refreshToken}`
        }
      });
      
      // Update token in local storage
      localStorage.setItem('token', response.data.access_token);
      return response.data.access_token;
    } catch (error) {
      // Clear everything
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      setCurrentUser(null);
      throw error;
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