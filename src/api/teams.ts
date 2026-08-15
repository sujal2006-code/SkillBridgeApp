import { apiClient } from './client';
import { ApiTeam, ApiTeamCandidateRecommendation } from '../types';

export interface CreateTeamPayload {
  name: string;
  description?: string;
  creator_id?: number;
  required_skill_ids?: number[];
}

export interface AddTeamMemberPayload {
  student_id: number;
  role?: string;
  status?: 'invited' | 'joined' | 'declined';
}

export const teamsApi = {
  /**
   * List all project teams
   */
  getTeams: () => {
    return apiClient.get<ApiTeam[]>('/api/teams');
  },

  /**
   * Create a new project team
   */
  createTeam: (payload: CreateTeamPayload) => {
    return apiClient.post<ApiTeam>('/api/teams', payload);
  },

  /**
   * Get team details by ID
   */
  getTeam: (teamId: number) => {
    return apiClient.get<ApiTeam>(`/api/teams/${teamId}`);
  },

  /**
   * Invite/Add a candidate student to a team
   */
  addTeamMember: (teamId: number, payload: AddTeamMemberPayload) => {
    return apiClient.post<ApiTeam>(`/api/teams/${teamId}/members`, payload);
  },

  /**
   * Get explainable candidate recommendations for a team based on real DB data
   */
  getTeamCandidates: (teamId: number) => {
    return apiClient.get<ApiTeamCandidateRecommendation[]>(`/api/teams/${teamId}/candidates`);
  },
};
