import { apiClient } from './client';
import { ApiTeam, ApiTeamCandidateRecommendation, ApiTeamInvitation, ApiTeamSkillRequirement } from '../types';

export interface CreateTeamPayload {
  name: string;
  project_name?: string;
  description?: string;
  creator_id?: number;
  required_skill_ids?: number[];
  required_domains?: string[];
  required_skills?: Partial<ApiTeamSkillRequirement>[];
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
   * Get teams where the current user is Leader or joined Member
   */
  getMyTeams: () => {
    return apiClient.get<ApiTeam[]>('/api/teams/my');
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
   * Update team skill requirements (leader only)
   */
  updateTeamRequirements: (teamId: number, requirements: Partial<ApiTeamSkillRequirement>[]) => {
    return apiClient.put<ApiTeam>(`/api/teams/${teamId}/requirements`, requirements);
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
   * Get explainable candidate recommendations for a team with role-specific gap matching
   */
  getTeamCandidates: (teamId: number, targetRole?: string, domain?: string) => {
    const params = new URLSearchParams();
    if (targetRole && targetRole !== 'All') params.append('target_role', targetRole);
    if (domain && domain !== 'All') params.append('domain', domain);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return apiClient.get<ApiTeamCandidateRecommendation[]>(`/api/teams/${teamId}/candidates${qs}`);
  },
};
