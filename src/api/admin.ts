import { apiClient } from './client';
import { ApiEvidence } from '../types';

export interface AdminStats {
  total_students: number;
  pending_evidence: number;
  verified_evidence: number;
  total_skills: number;
  total_internships: number;
  total_teams: number;
}

export interface AdminLoginResponse {
  status: string;
  token: string;
  username: string;
  message: string;
}

export const adminApi = {
  /**
   * Admin Authentication
   */
  login: (username: string, password: string) => {
    return apiClient.post<AdminLoginResponse>('/api/admin/login', { username, password });
  },

  /**
   * Fetch pending evidence queue
   */
  getPendingEvidence: () => {
    return apiClient.get<ApiEvidence[]>('/api/admin/evidence/pending');
  },

  /**
   * Approve evidence submission
   */
  approveEvidence: (evidenceId: number) => {
    return apiClient.post<ApiEvidence>(`/api/admin/evidence/${evidenceId}/approve`);
  },

  /**
   * Reject evidence submission
   */
  rejectEvidence: (evidenceId: number) => {
    return apiClient.post<ApiEvidence>(`/api/admin/evidence/${evidenceId}/reject`);
  },

  /**
   * Get platform statistics
   */
  getStats: () => {
    return apiClient.get<AdminStats>('/api/admin/stats');
  },
};
