import { apiClient } from './client';
import { ApiStudent } from '../types';

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
   * Retrieve a student by ID including their skills and evidence items
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
};
