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
   * Get unread notifications badge count
   */
  getUnreadCount: (studentId?: number) => {
    const query = studentId ? `?student_id=${studentId}` : '';
    return apiClient.get<{ unread_count: number }>(`/api/activities/unread-count${query}`);
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
