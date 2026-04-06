import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    const savedToken = localStorage.getItem('forge_token');
    if (savedToken) {
      setToken(savedToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
      fetchUser();
    } else {
      setLoading(false);
    }

    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        // Only auto-logout on 401 for specific auth-sensitive endpoints
        // Don't auto-logout during initial data loading to prevent iOS Safari race conditions
        const authEndpoints = ['/api/users/me', '/api/auth/'];
        const isAuthEndpoint = authEndpoints.some(ep => error.config?.url?.includes(ep));
        
        if (error.response?.status === 401 && isAuthEndpoint) {
          console.log('Auth interceptor: 401 on auth endpoint, logging out');
          logout();
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  const fetchUser = async (shouldLogoutOnError = true) => {
    try {
      const response = await axios.get(`${API}/users/me`);
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user:', error);
      // Only logout if explicitly requested and it's a 401 error
      if (shouldLogoutOnError && error.response?.status === 401) {
        logout();
      }
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    const { token: newToken, is_coach } = response.data;
    localStorage.setItem('forge_token', newToken);
    setToken(newToken);
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    await fetchUser();
    return { is_coach };  // Return coach status for redirect handling
  };

  const register = async (email, username, password, age, referralCode = null) => {
    const response = await axios.post(`${API}/auth/register`, {
      email,
      username,
      password,
      age: parseInt(age),
      referral_code: referralCode
    });
    const { token: newToken } = response.data;
    localStorage.setItem('forge_token', newToken);
    setToken(newToken);
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    
    // Fetch user but don't logout on failure - user is already registered
    try {
      await fetchUser(false); // Don't logout on error during registration
    } catch (error) {
      console.warn('Failed to fetch user after registration, continuing anyway:', error);
      // Set a minimal user object to prevent issues
      setUser({ id: response.data.user_id, email });
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('forge_token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading, fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
};