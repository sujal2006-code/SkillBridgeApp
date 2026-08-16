import React, { useState, useEffect } from 'react';
import { studentsApi, authApi } from '../api';
import { ApiStudentLoginResponse } from '../types';

export const validatePassword = (pwd: string): { isValid: boolean; message: string } => {
  const hasMinLength = pwd.length >= 6;
  const hasLetter = /[a-zA-Z]/.test(pwd);
  const hasNumber = /[0-9]/.test(pwd);
  const hasSpecial = /[^a-zA-Z0-9\s]/.test(pwd);

  if (!hasMinLength || !hasLetter || !hasNumber || !hasSpecial) {
    return {
      isValid: false,
      message: 'Password must have a minimum length of 6 characters and include at least 1 letter, 1 number, and 1 special character.',
    };
  }
  return { isValid: true, message: '' };
};

type AuthViewMode =
  | 'login'
  | 'register'
  | 'verify_register_otp'
  | 'forgot_password'
  | 'verify_reset_otp'
  | 'reset_password';

interface LoginViewProps {
  onLoginSuccess: (authData: ApiStudentLoginResponse) => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
  const [mode, setMode] = useState<AuthViewMode>('login');

  // Form Fields
  const [name, setName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('');
  const [confirmNewPassword, setConfirmNewPassword] = useState<string>('');
  const [otp, setOtp] = useState<string>('');
  const [resetToken, setResetToken] = useState<string>('');

  // Password Visibility
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false);
  const [showNewPassword, setShowNewPassword] = useState<boolean>(false);
  const [showConfirmNewPassword, setShowConfirmNewPassword] = useState<boolean>(false);

  // Status & Feedback
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Resend OTP Cooldown
  const [cooldown, setCooldown] = useState<number>(0);

  useEffect(() => {
    let timer: any;
    if (cooldown > 0) {
      timer = setInterval(() => setCooldown((prev) => prev - 1), 1000);
    }
    return () => clearInterval(timer);
  }, [cooldown]);

  const switchMode = (newMode: AuthViewMode) => {
    setMode(newMode);
    setErrorMessage(null);
    setSuccessMessage(null);
    setOtp('');
  };

  // 1. Handle Login
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = email.trim();
    const cleanPassword = password.trim();

    if (!cleanEmail || !cleanPassword) {
      setErrorMessage('Please enter both your email and password to continue.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const response = await studentsApi.loginStudent(cleanEmail, cleanPassword, 'login');
      onLoginSuccess(response);
    } catch (err: any) {
      setIsLoading(false);
      const msg = err.message || 'Authentication failed. Please check your credentials and try again.';
      setErrorMessage(msg);
    }
  };

  // 2. Handle Create Account -> Send Register OTP
  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanName = name.trim();
    const cleanEmail = email.trim().toLowerCase();
    const cleanPassword = password.trim();
    const cleanConfirm = confirmPassword.trim();

    if (!cleanName || !cleanEmail || !cleanPassword) {
      setErrorMessage('Please fill in all required fields.');
      return;
    }

    if (!cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      setErrorMessage('Please enter a valid Gmail / email address.');
      return;
    }

    // Password strength check
    const pwdValidation = validatePassword(cleanPassword);
    if (!pwdValidation.isValid) {
      setErrorMessage(pwdValidation.message);
      return;
    }

    // Confirm password match check
    if (cleanPassword !== cleanConfirm) {
      setErrorMessage('Passwords do not match.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const resp = await authApi.sendRegisterOtp({
        name: cleanName,
        email: cleanEmail,
        password: cleanPassword,
        confirm_password: cleanConfirm,
      });
      setIsLoading(false);
      setSuccessMessage(resp.message || 'Verification code sent to your email.');
      setCooldown(resp.cooldown_seconds || 60);
      setMode('verify_register_otp');
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Unable to send verification code. Please try again.');
    }
  };

  // 3. Handle Verify Register OTP -> Complete Account Creation
  const handleVerifyRegisterOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanOtp = otp.trim();
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanOtp || cleanOtp.length < 6) {
      setErrorMessage('Please enter the full 6-digit verification code.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await authApi.verifyRegisterOtp({
        email: cleanEmail,
        otp: cleanOtp,
      });
      onLoginSuccess(response);
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Invalid OTP. Please try again.');
    }
  };

  // 4. Handle Forgot Password -> Send Reset OTP
  const handleForgotPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanEmail || !cleanEmail.includes('@')) {
      setErrorMessage('Please enter your registered Gmail/email address.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const resp = await authApi.sendForgotPasswordOtp({ email: cleanEmail });
      setIsLoading(false);
      setSuccessMessage(resp.message || 'Password reset code sent to your email.');
      setCooldown(resp.cooldown_seconds || 60);
      setMode('verify_reset_otp');
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'No account found with this email.');
    }
  };

  // 5. Handle Verify Reset OTP -> Obtain Reset Token
  const handleVerifyResetOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanOtp = otp.trim();
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanOtp || cleanOtp.length < 6) {
      setErrorMessage('Please enter the full 6-digit verification code.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const resp = await authApi.verifyResetOtp({
        email: cleanEmail,
        otp: cleanOtp,
      });
      setIsLoading(false);
      if (resp.reset_token) {
        setResetToken(resp.reset_token);
        setMode('reset_password');
        setSuccessMessage('Verification successful. Please enter your new password.');
      } else {
        setErrorMessage('Verification failed. Please request a new OTP.');
      }
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Invalid OTP. Please try again.');
    }
  };

  // 6. Handle Reset Password Submission
  const handleResetPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = email.trim().toLowerCase();
    const cleanNewPassword = newPassword.trim();
    const cleanConfirmNewPassword = confirmNewPassword.trim();

    if (!cleanNewPassword || !cleanConfirmNewPassword) {
      setErrorMessage('Please fill in both password fields.');
      return;
    }

    const pwdValidation = validatePassword(cleanNewPassword);
    if (!pwdValidation.isValid) {
      setErrorMessage(pwdValidation.message);
      return;
    }

    if (cleanNewPassword !== cleanConfirmNewPassword) {
      setErrorMessage('Passwords do not match.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const resp = await authApi.resetPassword({
        email: cleanEmail,
        reset_token: resetToken,
        new_password: cleanNewPassword,
        confirm_password: cleanConfirmNewPassword,
      });
      setIsLoading(false);
      setPassword('');
      setConfirmPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
      setSuccessMessage(resp.message || 'Password updated successfully. Please log in with your new password.');
      setMode('login');
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Failed to update password. Please try again.');
    }
  };

  // 7. Resend OTP Action
  const handleResendOtp = async (purpose: 'register' | 'forgot_password') => {
    if (cooldown > 0) return;
    const cleanEmail = email.trim().toLowerCase();
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const resp = await authApi.resendOtp({ email: cleanEmail, purpose });
      setIsLoading(false);
      setSuccessMessage(resp.message || 'A new verification code has been sent.');
      setCooldown(resp.cooldown_seconds || 60);
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Unable to resend code.');
    }
  };

  // Demo Profile Auto-Fill Helper
  const handleQuickFillDemo = () => {
    setEmail('alex.rivera@stanford.edu');
    setPassword('stanford2026');
    setMode('login');
    setErrorMessage(null);
    setSuccessMessage(null);
  };

  return (
    <div className="min-h-screen bg-[#f7f9fb] flex flex-col justify-center items-center px-4 py-8 font-['Inter'] relative overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-cyan-100/50 rounded-full blur-3xl pointer-events-none -z-10"></div>
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-purple-100/40 rounded-full blur-3xl pointer-events-none -z-10"></div>

      {/* Main Authentication Card */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xl max-w-md w-full p-7 sm:p-9 relative transition-all duration-300">
        
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-13 h-13 rounded-2xl bg-[#00687a] text-white flex items-center justify-center shadow-xs mb-3.5">
            <span className="material-symbols-outlined text-[28px] material-symbols-fill">widgets</span>
          </div>
          <h1 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl font-bold text-[#191c1e] tracking-tight">
            SkillBridge
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-xs leading-relaxed">
            {mode === 'login' && 'Sign in to access your verified Digital Skill Passport & internship matches.'}
            {mode === 'register' && 'Create your account with Gmail to start building your verified passport.'}
            {mode === 'verify_register_otp' && 'Enter the 6-digit code sent to your Gmail inbox to verify your identity.'}
            {mode === 'forgot_password' && 'Enter your registered Gmail to receive a secure password reset code.'}
            {mode === 'verify_reset_otp' && 'Enter the reset code sent to your Gmail inbox.'}
            {mode === 'reset_password' && 'Create a strong new password for your SkillBridge account.'}
          </p>
        </div>

        {/* Tab Switcher (Visible on Login / Register) */}
        {(mode === 'login' || mode === 'register') && (
          <div className="flex bg-slate-100 p-1 rounded-xl mb-6">
            <button
              type="button"
              onClick={() => switchMode('login')}
              className={`flex-1 py-2.5 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                mode === 'login'
                  ? 'bg-white text-[#00687a] shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              id="tab-login"
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => switchMode('register')}
              className={`flex-1 py-2.5 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                mode === 'register'
                  ? 'bg-white text-[#00687a] shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              id="tab-register"
            >
              Create Account
            </button>
          </div>
        )}

        {/* Success Alert */}
        {successMessage && (
          <div
            id="auth-success-alert"
            className="mb-5 p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-medium flex items-start gap-2.5 animate-fadeIn"
          >
            <span className="material-symbols-outlined text-[18px] text-emerald-600 shrink-0 mt-0.5">
              check_circle
            </span>
            <span className="leading-snug">{successMessage}</span>
          </div>
        )}

        {/* Error / Validation Notification */}
        {errorMessage && (
          <div
            id="auth-error-alert"
            className="mb-5 p-3.5 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs font-medium flex flex-col gap-1.5 animate-fadeIn"
          >
            <div className="flex items-start gap-2.5">
              <span className="material-symbols-outlined text-[18px] text-red-600 shrink-0 mt-0.5">
                error
              </span>
              <span className="leading-snug">{errorMessage}</span>
            </div>
            {errorMessage.toLowerCase().includes('already exists') && mode === 'register' && (
              <button
                type="button"
                onClick={() => switchMode('login')}
                className="self-start ml-7 text-xs font-bold text-[#00687a] hover:underline cursor-pointer flex items-center gap-1 mt-0.5"
              >
                <span>Switch to Sign In</span>
                <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
              </button>
            )}
          </div>
        )}

        {/* ========================================================= */}
        {/* 1. SIGN IN FORM */}
        {/* ========================================================= */}
        {mode === 'login' && (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label htmlFor="login-email-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Gmail / Email Address
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <span className="material-symbols-outlined text-[18px]">mail</span>
                </span>
                <input
                  id="login-email-input"
                  type="text"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errorMessage) setErrorMessage(null);
                  }}
                  placeholder="e.g. alex.rivera@gmail.com"
                  disabled={isLoading}
                  autoFocus
                  required
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label htmlFor="login-password-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => switchMode('forgot_password')}
                  className="text-xs font-semibold text-[#00687a] hover:underline cursor-pointer"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <span className="material-symbols-outlined text-[18px]">lock</span>
                </span>
                <input
                  id="login-password-input"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errorMessage) setErrorMessage(null);
                  }}
                  placeholder="Enter your password"
                  disabled={isLoading}
                  required
                  className="w-full pl-10 pr-11 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none cursor-pointer"
                  tabIndex={-1}
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            <div className="pt-2">
              <button
                id="login-submit-button"
                type="submit"
                disabled={isLoading || !email.trim() || !password.trim()}
                className="w-full py-3.5 bg-[#00687a] hover:bg-[#004e5c] text-white text-sm font-bold rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>Signing In...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In & Resume</span>
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}

        {/* ========================================================= */}
        {/* 2. CREATE ACCOUNT FORM (Step 1: Details) */}
        {/* ========================================================= */}
        {mode === 'register' && (
          <form onSubmit={handleRegisterSubmit} className="space-y-3.5">
            <div>
              <label htmlFor="reg-name-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Full Name
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <span className="material-symbols-outlined text-[18px]">person</span>
                </span>
                <input
                  id="reg-name-input"
                  type="text"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    if (errorMessage) setErrorMessage(null);
                  }}
                  placeholder="e.g. Maya Lin"
                  disabled={isLoading}
                  autoFocus
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
              </div>
            </div>

            <div>
              <label htmlFor="reg-email-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Gmail / Email Address
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <span className="material-symbols-outlined text-[18px]">mail</span>
                </span>
                <input
                  id="reg-email-input"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errorMessage) setErrorMessage(null);
                  }}
                  placeholder="e.g. maya.lin@gmail.com"
                  disabled={isLoading}
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
              </div>
            </div>

            <div>
              <label htmlFor="reg-password-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <span className="material-symbols-outlined text-[18px]">lock</span>
                </span>
                <input
                  id="reg-password-input"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errorMessage) setErrorMessage(null);
                  }}
                  placeholder="At least 6 chars with letters, numbers & symbols"
                  disabled={isLoading}
                  required
                  className="w-full pl-10 pr-11 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none cursor-pointer"
                  tabIndex={-1}
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            <div>
              <label htmlFor="reg-confirm-password-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <span className="material-symbols-outlined text-[18px]">lock_reset</span>
                </span>
                <input
                  id="reg-confirm-password-input"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value);
                    if (errorMessage) setErrorMessage(null);
                  }}
                  placeholder="Re-enter password"
                  disabled={isLoading}
                  required
                  className="w-full pl-10 pr-11 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none cursor-pointer"
                  tabIndex={-1}
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showConfirmPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5 flex items-center gap-1">
                <span className="material-symbols-outlined text-[13px] text-slate-400">info</span>
                <span>Min 6 characters with $\ge$1 letter, $\ge$1 number & $\ge$1 symbol.</span>
              </p>
            </div>

            <div className="pt-2">
              <button
                id="register-submit-button"
                type="submit"
                disabled={isLoading || !name.trim() || !email.trim() || !password.trim() || !confirmPassword.trim()}
                className="w-full py-3.5 bg-[#00687a] hover:bg-[#004e5c] text-white text-sm font-bold rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>Sending Verification Code...</span>
                  </>
                ) : (
                  <>
                    <span>Continue & Send OTP</span>
                    <span className="material-symbols-outlined text-[18px]">mail</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}

        {/* ========================================================= */}
        {/* 3. VERIFY REGISTRATION OTP (Step 2: Enter OTP) */}
        {/* ========================================================= */}
        {mode === 'verify_register_otp' && (
          <form onSubmit={handleVerifyRegisterOtp} className="space-y-5">
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-center">
              <span className="material-symbols-outlined text-[32px] text-[#00687a] mb-1">
                mark_email_read
              </span>
              <p className="text-xs text-slate-500">
                Verification code sent to:
              </p>
              <p className="text-sm font-bold text-slate-800 break-all mt-0.5">
                {email}
              </p>
            </div>

            <div>
              <label htmlFor="register-otp-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 text-center">
                Enter 6-Digit Code
              </label>
              <input
                id="register-otp-input"
                type="text"
                maxLength={6}
                value={otp}
                onChange={(e) => {
                  setOtp(e.target.value.replace(/\D/g, ''));
                  if (errorMessage) setErrorMessage(null);
                }}
                placeholder="123456"
                disabled={isLoading}
                autoFocus
                required
                className="w-full py-3 text-center text-2xl font-bold tracking-[8px] bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all font-mono"
              />
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <button
                type="button"
                onClick={() => switchMode('register')}
                className="text-slate-500 hover:text-slate-800 font-medium flex items-center gap-1 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[15px]">arrow_back</span>
                <span>Change Email</span>
              </button>

              <button
                type="button"
                onClick={() => handleResendOtp('register')}
                disabled={cooldown > 0 || isLoading}
                className="text-[#00687a] font-bold hover:underline disabled:opacity-50 disabled:no-underline cursor-pointer"
              >
                {cooldown > 0 ? `Resend Code in ${cooldown}s` : 'Resend Code'}
              </button>
            </div>

            <div>
              <button
                id="verify-register-otp-button"
                type="submit"
                disabled={isLoading || otp.trim().length < 6}
                className="w-full py-3.5 bg-[#00687a] hover:bg-[#004e5c] text-white text-sm font-bold rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>Verifying Code...</span>
                  </>
                ) : (
                  <>
                    <span>Verify & Create Passport</span>
                    <span className="material-symbols-outlined text-[18px]">verified</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}

        {/* ========================================================= */}
        {/* 4. FORGOT PASSWORD (Enter Email) */}
        {/* ========================================================= */}
        {mode === 'forgot_password' && (
          <form onSubmit={handleForgotPasswordSubmit} className="space-y-4">
            <div>
              <label htmlFor="forgot-email-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Registered Gmail / Email
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <span className="material-symbols-outlined text-[18px]">mail</span>
                </span>
                <input
                  id="forgot-email-input"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errorMessage) setErrorMessage(null);
                  }}
                  placeholder="e.g. yourname@gmail.com"
                  disabled={isLoading}
                  autoFocus
                  required
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
              </div>
            </div>

            <div className="pt-2">
              <button
                id="send-forgot-otp-button"
                type="submit"
                disabled={isLoading || !email.trim()}
                className="w-full py-3.5 bg-[#00687a] hover:bg-[#004e5c] text-white text-sm font-bold rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>Sending Reset Code...</span>
                  </>
                ) : (
                  <>
                    <span>Send Reset Code</span>
                    <span className="material-symbols-outlined text-[18px]">send</span>
                  </>
                )}
              </button>
            </div>

            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => switchMode('login')}
                className="text-xs font-bold text-slate-600 hover:text-slate-900 cursor-pointer flex items-center justify-center gap-1 mx-auto"
              >
                <span className="material-symbols-outlined text-[15px]">arrow_back</span>
                <span>Back to Sign In</span>
              </button>
            </div>
          </form>
        )}

        {/* ========================================================= */}
        {/* 5. VERIFY RESET OTP */}
        {/* ========================================================= */}
        {mode === 'verify_reset_otp' && (
          <form onSubmit={handleVerifyResetOtp} className="space-y-5">
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-center">
              <span className="material-symbols-outlined text-[32px] text-[#00687a] mb-1">
                lock_reset
              </span>
              <p className="text-xs text-slate-500">
                Password reset code sent to:
              </p>
              <p className="text-sm font-bold text-slate-800 break-all mt-0.5">
                {email}
              </p>
            </div>

            <div>
              <label htmlFor="reset-otp-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 text-center">
                Enter 6-Digit Reset Code
              </label>
              <input
                id="reset-otp-input"
                type="text"
                maxLength={6}
                value={otp}
                onChange={(e) => {
                  setOtp(e.target.value.replace(/\D/g, ''));
                  if (errorMessage) setErrorMessage(null);
                }}
                placeholder="123456"
                disabled={isLoading}
                autoFocus
                required
                className="w-full py-3 text-center text-2xl font-bold tracking-[8px] bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all font-mono"
              />
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <button
                type="button"
                onClick={() => switchMode('forgot_password')}
                className="text-slate-500 hover:text-slate-800 font-medium flex items-center gap-1 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[15px]">arrow_back</span>
                <span>Change Email</span>
              </button>

              <button
                type="button"
                onClick={() => handleResendOtp('forgot_password')}
                disabled={cooldown > 0 || isLoading}
                className="text-[#00687a] font-bold hover:underline disabled:opacity-50 disabled:no-underline cursor-pointer"
              >
                {cooldown > 0 ? `Resend Code in ${cooldown}s` : 'Resend Code'}
              </button>
            </div>

            <div>
              <button
                id="verify-reset-otp-button"
                type="submit"
                disabled={isLoading || otp.trim().length < 6}
                className="w-full py-3.5 bg-[#00687a] hover:bg-[#004e5c] text-white text-sm font-bold rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>Verifying Code...</span>
                  </>
                ) : (
                  <>
                    <span>Verify Code</span>
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}

        {/* ========================================================= */}
        {/* 6. RESET PASSWORD (Create New Password) */}
        {/* ========================================================= */}
        {mode === 'reset_password' && (
          <form onSubmit={handleResetPasswordSubmit} className="space-y-4">
            <div>
              <label htmlFor="new-password-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                New Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <span className="material-symbols-outlined text-[18px]">lock</span>
                </span>
                <input
                  id="new-password-input"
                  type={showNewPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => {
                    setNewPassword(e.target.value);
                    if (errorMessage) setErrorMessage(null);
                  }}
                  placeholder="Enter new password"
                  disabled={isLoading}
                  autoFocus
                  required
                  className="w-full pl-10 pr-11 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none cursor-pointer"
                  tabIndex={-1}
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showNewPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            <div>
              <label htmlFor="confirm-new-password-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Confirm New Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <span className="material-symbols-outlined text-[18px]">lock_reset</span>
                </span>
                <input
                  id="confirm-new-password-input"
                  type={showConfirmNewPassword ? 'text' : 'password'}
                  value={confirmNewPassword}
                  onChange={(e) => {
                    setConfirmNewPassword(e.target.value);
                    if (errorMessage) setErrorMessage(null);
                  }}
                  placeholder="Re-enter new password"
                  disabled={isLoading}
                  required
                  className="w-full pl-10 pr-11 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmNewPassword(!showConfirmNewPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none cursor-pointer"
                  tabIndex={-1}
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showConfirmNewPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5 flex items-center gap-1">
                <span className="material-symbols-outlined text-[13px] text-slate-400">info</span>
                <span>Min 6 characters with $\ge$1 letter, $\ge$1 number & $\ge$1 symbol.</span>
              </p>
            </div>

            <div className="pt-2">
              <button
                id="save-new-password-button"
                type="submit"
                disabled={isLoading || !newPassword.trim() || !confirmNewPassword.trim()}
                className="w-full py-3.5 bg-[#00687a] hover:bg-[#004e5c] text-white text-sm font-bold rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>Saving New Password...</span>
                  </>
                ) : (
                  <>
                    <span>Update Password in Database</span>
                    <span className="material-symbols-outlined text-[18px]">save</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}

        {/* Demo Fast-Fill Helper for Testing (Only on Login) */}
        {mode === 'login' && (
          <div className="mt-6 pt-5 border-t border-slate-100 flex flex-col items-center">
            <p className="text-[11px] text-slate-400 text-center mb-1.5">
              Need a quick demo profile?
            </p>
            <button
              type="button"
              onClick={handleQuickFillDemo}
              className="text-xs font-semibold text-[#00687a] hover:text-[#004e5c] hover:underline flex items-center gap-1 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[14px]">bolt</span>
              <span>Use Demo Profile (Alex Rivera)</span>
            </button>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <p className="text-xs text-slate-400 text-center mt-6">
        Protected with PBKDF2 cryptography & Email OTP • SkillBridge Verifiable Credential Protocol
      </p>
    </div>
  );
};
