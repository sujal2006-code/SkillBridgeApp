import { apiClient } from './client';
import { ApiActivity } from '../types';

export interface CreateActivityPayload {
  student_id?: number;
  activity_type: string;
  title: string;
  description?: string;
  icon?: string;
  related_entity_type?: string;
  related_entity_id?: number;
}

export const activitiesApi = {
  /**
   * Fetch persistent activity and notification log
   */
  getActivities: (studentId?: number, limit = 50) => {
    const query = studentId ? `?student_id=${studentId}&limit=${limit}` : `?limit=${limit}`;
    return apiClient.get<ApiActivity[]>(`/api/activities${query}`);
  },

  /**
   * Log a new activity item
   */
  createActivity: (payload: CreateActivityPayload) => {
    return apiClient.post<ApiActivity>('/api/activities', payload);
  },

  /**
   * Mark activity notification as read
   */
  markRead: (activityId: number) => {
    return apiClient.patch<ApiActivity>(`/api/activities/${activityId}/read`);
  },
};
