import axios from 'axios';

// Create an Axios instance with default configs
const API = axios.create({
  baseURL: 'http://localhost:5001', // Flask backend URL without API prefix
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add an interceptor to add the auth token to requests
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      console.log('Adding auth token to request', config.url);
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.log('No auth token available for request', config.url);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle token refresh
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

API.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Log the error for debugging
    console.error('API Error:', error.response?.status, error.response?.data);
    
    // If the error is due to an expired token
    if (error.response && error.response.status === 401 && 
        error.response.data.error_type === 'token_expired' && 
        !originalRequest._retry) {
      
      if (isRefreshing) {
        // Wait for the token to be refreshed
        try {
          const token = await new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          });
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return axios(originalRequest);
        } catch (err) {
          return Promise.reject(err);
        }
      }
      
      originalRequest._retry = true;
      isRefreshing = true;
      
      try {
        // Get the refresh token
        const refreshToken = localStorage.getItem('refreshToken');
        
        if (!refreshToken) {
          // No refresh token, redirect to login
          window.location.href = '/login';
          return Promise.reject(error);
        }
        
        // Call the refresh token endpoint with the correct API path
        const response = await axios.post(`${API.defaults.baseURL}/api/auth/refresh`, {}, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        });
        
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        
        // Update all requests in the queue
        processQueue(null, access_token);
        
        // Update the original request & retry
        originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
        
        return axios(originalRequest);
      } catch (err) {
        // If refresh fails, redirect to login
        processQueue(err, null);
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }
    
    // If it's a different 401 error (not token expired)
    if (error.response && error.response.status === 401) {
      // Clear tokens and redirect to login if auth completely fails
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default API; 