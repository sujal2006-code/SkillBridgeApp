import { apiClient } from './client';
import { ApiSkill } from '../types';

export interface CreateSkillPayload {
  name: string;
  category: string;
  description?: string;
}

export const skillsApi = {
  /**
   * Retrieve all skills with optional category filter
   */
  getSkills: (category?: string) => {
    const query = category ? `?category=${encodeURIComponent(category)}` : '';
    return apiClient.get<ApiSkill[]>(`/api/skills${query}`);
  },

  /**
   * Create a new skill
   */
  createSkill: (payload: CreateSkillPayload) => {
    return apiClient.post<ApiSkill>('/api/skills', payload);
  },
};
