import { apiClient } from './client';
import { ApiStudentRecommendationsResponse, ApiRecommendation, ApiInternship } from '../types';

export const recommendationsApi = {
  /**
   * Retrieve deterministic recommendations directly for the authenticated student via verified JWT
   */
  getMyRecommendations: () => {
    return apiClient.get<ApiStudentRecommendationsResponse>('/api/recommendations/me');
  },

  /**
   * Retrieve deterministic, explainable internship recommendations for a given student
   */
  getStudentRecommendations: (studentId: number) => {
    return apiClient.get<ApiStudentRecommendationsResponse>(`/api/recommendations/students/${studentId}`);
  },

  /**
   * Alias for getStudentRecommendations for backward compatibility
   */
  getRecommendationsForStudent: (studentId: number) => {
    return apiClient.get<ApiStudentRecommendationsResponse>(`/api/recommendations/students/${studentId}`);
  },

  /**
   * Retrieve a single detailed match analysis for a specific student and internship pair
   */
  getSingleRecommendation: (studentId: number, internshipId: number) => {
    return apiClient.get<ApiRecommendation>(`/api/recommendations/students/${studentId}/internships/${internshipId}`);
  },

  /**
   * Safe fallback to retrieve all internships list
   */
  getInternships: (skip = 0, limit = 50) => {
    return apiClient.get<ApiInternship[]>(`/api/internships?skip=${skip}&limit=${limit}`);
  },
};
