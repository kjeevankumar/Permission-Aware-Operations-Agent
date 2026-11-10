import api from './api';

export const chatService = {
  /**
   * Send a natural language query to the backend agent at /chat
   */
  async sendMessage(message) {
    try {
      const response = await api.post('/chat', { message });
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      if (error.response) {
        return {
          success: false,
          status: error.response.status,
          detail: error.response.data?.detail || error.response.data,
        };
      }
      return {
        success: false,
        status: 0,
        detail: error.message || 'Network connection failed',
      };
    }
  },
};
