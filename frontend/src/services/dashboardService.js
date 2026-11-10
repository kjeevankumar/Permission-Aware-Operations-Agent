import api from './api';

export const dashboardService = {
  /**
   * Fetch aggregate system metrics from /system/stats
   */
  async getStats() {
    const response = await api.get('/system/stats');
    return response.data;
  },
};
