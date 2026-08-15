import { apiClient } from './client';
import { ApiStudentRecommendationsResponse, ApiRecommendation } from '../types';

export const recommendationsApi = {
  /**
   * Retrieve deterministic, explainable internship recommendations for a given student
   */
  getStudentRecommendations: (studentId: number) => {
    return apiClient.get<ApiStudentRecommendationsResponse>(`/api/recommendations/students/${studentId}`);
  },

  /**
   * Retrieve a single detailed match analysis for a specific student and internship pair
   */
  getSingleRecommendation: (studentId: number, internshipId: number) => {
    return apiClient.get<ApiRecommendation>(`/api/recommendations/students/${studentId}/internships/${internshipId}`);
  },
};
