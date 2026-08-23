import { apiClient } from './client';
import { ApiTeam, ApiTeamCandidateRecommendation, ApiTeamInvitation } from '../types';

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

export interface CreateTeamInvitationPayload {
  recipient_id: number;
  role?: string;
  message?: string;
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
   * Invite/Add a candidate student directly to a team
   */
  addTeamMember: (teamId: number, payload: AddTeamMemberPayload) => {
    return apiClient.post<ApiTeam>(`/api/teams/${teamId}/members`, payload);
  },

  /**
   * Send a persistent team invitation
   */
  createTeamInvitation: (teamId: number, payload: CreateTeamInvitationPayload) => {
    return apiClient.post<ApiTeamInvitation>(`/api/teams/${teamId}/invitations`, payload);
  },

  /**
   * Get pending invitations for the authenticated student
   */
  getPendingInvitations: () => {
    return apiClient.get<ApiTeamInvitation[]>('/api/teams/invitations/pending');
  },

  /**
   * Accept a pending team invitation
   */
  acceptInvitation: (invitationId: number) => {
    return apiClient.post<ApiTeamInvitation>(`/api/teams/invitations/${invitationId}/accept`, {});
  },

  /**
   * Reject a pending team invitation
   */
  rejectInvitation: (invitationId: number) => {
    return apiClient.post<ApiTeamInvitation>(`/api/teams/invitations/${invitationId}/reject`, {});
  },

  /**
   * Get explainable candidate recommendations for a team based on real DB data and complementarity
   */
  getTeamCandidates: (teamId: number) => {
    return apiClient.get<ApiTeamCandidateRecommendation[]>(`/api/teams/${teamId}/candidates`);
  },
};
