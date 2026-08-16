import { apiClient } from './client';
import { ApiStudentLoginResponse, ApiOtpResponse } from '../types';

export interface RegisterOtpPayload {
  name: string;
  email: string;
  password: string;
  confirm_password?: string;
}

export interface VerifyRegisterOtpPayload {
  email: string;
  otp: string;
}

export interface ForgotPasswordOtpPayload {
  email: string;
}

export interface VerifyResetOtpPayload {
  email: string;
  otp: string;
}

export interface ResetPasswordPayload {
  email: string;
  reset_token: string;
  new_password: string;
  confirm_password?: string;
}

export interface ResendOtpPayload {
  email: string;
  purpose: 'register' | 'forgot_password';
}

export const authApi = {
  /**
   * Send 6-digit OTP to user's Gmail for new registration
   */
  sendRegisterOtp: (payload: RegisterOtpPayload) => {
    return apiClient.post<ApiOtpResponse>('/api/auth/register-otp', payload);
  },

  /**
   * Verify registration OTP and create persistent PostgreSQL account
   */
  verifyRegisterOtp: (payload: VerifyRegisterOtpPayload) => {
    return apiClient.post<ApiStudentLoginResponse>('/api/auth/verify-register-otp', payload);
  },

  /**
   * Send 6-digit OTP to registered Gmail for password recovery
   */
  sendForgotPasswordOtp: (payload: ForgotPasswordOtpPayload) => {
    return apiClient.post<ApiOtpResponse>('/api/auth/forgot-password-otp', payload);
  },

  /**
   * Verify password reset OTP and obtain reset token
   */
  verifyResetOtp: (payload: VerifyResetOtpPayload) => {
    return apiClient.post<ApiOtpResponse>('/api/auth/verify-reset-otp', payload);
  },

  /**
   * Reset password in PostgreSQL using verified reset token
   */
  resetPassword: (payload: ResetPasswordPayload) => {
    return apiClient.post<ApiOtpResponse>('/api/auth/reset-password', payload);
  },

  /**
   * Resend fresh OTP with cooldown
   */
  resendOtp: (payload: ResendOtpPayload) => {
    return apiClient.post<ApiOtpResponse>('/api/auth/resend-otp', payload);
  },
};
