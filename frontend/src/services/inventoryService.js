import api from './api';

export const inventoryService = {
  /**
   * Fetch inventory items with optional filters
   */
  async getInventory(params = {}) {
    const response = await api.get('/inventory', { params });
    return response.data;
  },

  /**
   * Fetch single item by ID
   */
  async getItem(id) {
    const response = await api.get(`/inventory/${id}`);
    return response.data;
  },
};
