import { apiClient } from './client';
import { ApiStudent, ApiStudentLoginResponse } from '../types';

export interface CreateStudentPayload {
  name: string;
  email: string;
  university: string;
  graduation_year: number;
}

export const studentsApi = {
  /**
   * List all registered students
   */
  getStudents: (skip = 0, limit = 50) => {
    return apiClient.get<ApiStudent[]>(`/api/students?skip=${skip}&limit=${limit}`);
  },

  /**
   * Retrieve the authenticated student's profile directly using verified JWT token
   */
  getMyProfile: () => {
    return apiClient.get<ApiStudent>('/api/students/me');
  },

  /**
   * Retrieve a student by ID including their skills and evidence items (authenticated)
   */
  getStudent: (studentId: number) => {
    return apiClient.get<ApiStudent>(`/api/students/${studentId}`);
  },

  /**
   * Register a new student
   */
  createStudent: (payload: CreateStudentPayload) => {
    return apiClient.post<ApiStudent>('/api/students', payload);
  },

  /**
   * Onboard or retrieve existing student by name
   */
  onboardStudent: (name: string, email?: string, university?: string) => {
    return apiClient.post<ApiStudent>('/api/students/onboard', { name, email, university });
  },

  /**
   * Secure login or account registration with password
   */
  loginStudent: (name: string, password: string, mode: 'login' | 'register' | 'auto' = 'auto') => {
    return apiClient.post<ApiStudentLoginResponse>('/api/students/login', { name, password, mode });
  },

  /**
   * Persist current student navigation and workflow state to resume seamlessly
   */
  updateStudentState: (studentId: number, lastScreen: string, lastStateJson?: string) => {
    return apiClient.patch<ApiStudent>(`/api/students/${studentId}/state`, {
      last_screen: lastScreen,
      last_state_json: lastStateJson,
    });
  },

  /**
   * Persist authenticated student navigation and workflow state
   */
  updateMyState: (lastScreen: string, lastStateJson?: string) => {
    return apiClient.patch<ApiStudent>('/api/students/me/state', {
      last_screen: lastScreen,
      last_state_json: lastStateJson,
    });
  },
};


