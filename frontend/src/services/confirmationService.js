import api from './api';

export const confirmationService = {
  /**
   * Request a dry-run preview and diff calculation
   */
  async createPreview(payload) {
    const response = await api.post('/confirmations/preview', payload);
    return response.data;
  },

  /**
   * List all staged pending operations awaiting confirmation in this hospital
   */
  async getPending() {
    const response = await api.get('/confirmations/pending');
    return response.data;
  },

  /**
   * Confirm and atomically execute a staged pending operation
   */
  async confirm(operationId, reason = '') {
    const response = await api.post(`/confirmations/${operationId}/confirm`, {
      reason,
    });
    return response.data;
  },

  /**
   * Reject a staged pending operation without applying changes
   */
  async reject(operationId, reason = '') {
    const response = await api.post(`/confirmations/${operationId}/reject`, {
      reason,
    });
    return response.data;
  },
};
