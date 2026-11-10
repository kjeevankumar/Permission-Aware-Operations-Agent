import api from './api';

export const authService = {
  /**
   * Authenticate user with JSON payload to /auth/login
   */
  async login(username, password) {
    const response = await api.post('/auth/login', {
      username: username.trim(),
      password: password.trim(),
    });
    const { access_token } = response.data;
    if (access_token) {
      localStorage.setItem('token', access_token);
    }
    return response.data;
  },

  /**
   * Retrieve authenticated user security context from /auth/me
   */
  async getMe() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  /**
   * Log out current user and clear token
   */
  logout() {
    localStorage.removeItem('token');
  },

  getToken() {
    return localStorage.getItem('token');
  },
};
