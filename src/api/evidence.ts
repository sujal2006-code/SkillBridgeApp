import { apiClient } from './client';
import { ApiEvidence } from '../types';

export interface CreateEvidencePayload {
  student_id: number;
  skill_id?: number | null;
  evidence_type: 'coursework' | 'project' | 'competition' | 'certificate' | 'internship' | string;
  title: string;
  description?: string | null;
  issuer?: string | null;
  verification_status?: 'verified' | 'pending' | 'rejected' | string;
  evidence_url?: string | null;
}

export const evidenceApi = {
  /**
   * Submit new evidence item for a student
   */
  createEvidence: (payload: CreateEvidencePayload) => {
    return apiClient.post<ApiEvidence>('/api/evidence', payload);
  },

  /**
   * List all evidence submitted across students (for verification queue / admin)
   */
  getAllEvidence: (skip = 0, limit = 100) => {
    return apiClient.get<ApiEvidence[]>(`/api/evidence?skip=${skip}&limit=${limit}`);
  },

  /**
   * List evidence submitted by a specific student
   */
  getStudentEvidence: (studentId: number) => {
    return apiClient.get<ApiEvidence[]>(`/api/students/${studentId}/evidence`);
  },

  /**
   * Update evidence verification status (admin audit)
   */
  updateEvidenceStatus: (evidenceId: number, status: 'verified' | 'pending' | 'rejected' | string) => {
    return apiClient.patch<ApiEvidence>(`/api/evidence/${evidenceId}/status`, {
      verification_status: status,
    });
  },
};
