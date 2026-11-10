import api from './api';

export const auditService = {
  /**
   * Fetch immutable audit logs scoped to the hospital
   */
  async getAuditLogs(params = {}) {
    const response = await api.get('/audit', { params });
    return response.data;
  },
};
