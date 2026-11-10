import api from './api';

export const billsService = {
  /**
   * Fetch bills with optional status and pagination
   */
  async getBills(params = {}) {
    const response = await api.get('/bills', { params });
    return response.data;
  },

  /**
   * Fetch single bill by ID
   */
  async getBill(id) {
    const response = await api.get(`/bills/${id}`);
    return response.data;
  },
};
