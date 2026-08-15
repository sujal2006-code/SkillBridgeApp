import { apiClient } from './client';
import { ApiInternship } from '../types';

export interface CreateInternshipSkillPayload {
  skill_id: number;
  required?: boolean;
  minimum_proficiency?: string;
}

export interface CreateInternshipPayload {
  title: string;
  company: string;
  description: string;
  location: string;
  required_skills?: string[];
  preferred_skills?: string[];
  skills_required?: CreateInternshipSkillPayload[];
}

export const internshipsApi = {
  /**
   * Retrieve all internships with required and preferred skills
   */
  getInternships: (skip = 0, limit = 50) => {
    return apiClient.get<ApiInternship[]>(`/api/internships?skip=${skip}&limit=${limit}`);
  },

  /**
   * Retrieve single internship by ID
   */
  getInternship: (internshipId: number) => {
    return apiClient.get<ApiInternship>(`/api/internships/${internshipId}`);
  },

  /**
   * Create a new internship
   */
  createInternship: (payload: CreateInternshipPayload) => {
    return apiClient.post<ApiInternship>('/api/internships', payload);
  },
};
