import React, { useState } from 'react';
import { studentsApi } from '../api';
import { ApiStudentLoginResponse } from '../types';

interface LoginViewProps {
  onLoginSuccess: (authData: ApiStudentLoginResponse) => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');

  // Form Fields
  const [name, setName] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');

  // Password Visibility
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false);

  // Status & Feedback
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const switchMode = (newMode: 'login' | 'register') => {
    setMode(newMode);
    setErrorMessage(null);
    setSuccessMessage(null);
    setPassword('');
    setConfirmPassword('');
  };

  // Handle Login Submit (Sign In)
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanName = name.trim();
    const cleanPassword = password.trim();

    if (!cleanName) {
      setErrorMessage('Name is required.');
      return;
    }

    if (!cleanPassword) {
      setErrorMessage('Password is required.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const response = await studentsApi.loginStudent(cleanName, cleanPassword, 'login');
      onLoginSuccess(response);
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Incorrect name.');
    }
  };

  // Handle Register Submit (Create Account)
  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanName = name.trim();
    const cleanPassword = password.trim();
    const cleanConfirm = confirmPassword.trim();

    if (!cleanName) {
      setErrorMessage('Name is required.');
      return;
    }

    if (!cleanPassword) {
      setErrorMessage('Password is required.');
      return;
    }

    if (!cleanConfirm) {
      setErrorMessage('Confirm Password is required.');
      return;
    }

    if (cleanPassword !== cleanConfirm) {
      setErrorMessage('Passwords do not match.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const response = await studentsApi.loginStudent(cleanName, cleanPassword, 'register', cleanConfirm);
      onLoginSuccess(response);
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Account already exists. Please log in.');
    }
  };

  // Demo Profile Fast-Fill Helper for Testing
  const handleQuickFillDemo = () => {
    setName('Alex Rivera');
    setPassword('stanford2026');
    setMode('login');
    setErrorMessage(null);
    setSuccessMessage(null);
  };

  return (
    <div className="min-h-screen bg-[#f7f9fb] flex flex-col justify-center items-center px-4 py-8 font-['Inter'] relative overflow-hidden">
      {/* Subtle Background Ambience */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-cyan-100/40 rounded-full blur-3xl pointer-events-none -z-10"></div>
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-slate-200/40 rounded-full blur-3xl pointer-events-none -z-10"></div>

      {/* Main Authentication Card */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xl max-w-md w-full p-7 sm:p-9 relative transition-all duration-300">
        
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-13 h-13 rounded-2xl bg-[#00687a] text-white flex items-center justify-center shadow-xs mb-3.5">
            <span className="material-symbols-outlined text-[28px] material-symbols-fill">widgets</span>
          </div>
          <h1 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl font-bold text-[#191c1e] tracking-tight">
            {mode === 'login' ? 'Welcome back to SkillBridge' : 'Create your SkillBridge account'}
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-xs leading-relaxed">
            {mode === 'login'
              ? 'Sign in to access your verified Digital Skill Passport & opportunity matches.'
              : 'Build your verified Digital Skill Passport and connect with top internships.'}
          </p>
        </div>

        {/* Tab Switcher */}
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
        {/* SIGN IN FORM */}
        {/* ========================================================= */}
        {mode === 'login' && (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label htmlFor="login-name-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Name
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <span className="material-symbols-outlined text-[18px]">person</span>
                </span>
                <input
                  id="login-name-input"
                  type="text"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    if (errorMessage) setErrorMessage(null);
                  }}
                  placeholder="e.g. Alex Rivera"
                  disabled={isLoading}
                  autoFocus
                  required
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
              </div>
            </div>

            <div>
              <label htmlFor="login-password-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Password
              </label>
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
                disabled={isLoading || !name.trim() || !password.trim()}
                className="w-full py-3.5 bg-[#00687a] hover:bg-[#004e5c] text-white text-sm font-bold rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>Signing In...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In</span>
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}

        {/* ========================================================= */}
        {/* CREATE ACCOUNT FORM */}
        {/* ========================================================= */}
        {mode === 'register' && (
          <form onSubmit={handleRegisterSubmit} className="space-y-4">
            <div>
              <label htmlFor="reg-name-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Name
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
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
              </div>
            </div>

            <div>
              <label htmlFor="reg-password-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
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
                  placeholder="Create your password"
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

            <div>
              <label htmlFor="reg-confirm-password-input" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
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
                  placeholder="Re-enter password to confirm"
                  disabled={isLoading}
                  required
                  className="w-full pl-10 pr-11 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none cursor-pointer"
                  tabIndex={-1}
                  title={showConfirmPassword ? 'Hide password' : 'Show password'}
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showConfirmPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            <div className="pt-2">
              <button
                id="register-submit-button"
                type="submit"
                disabled={isLoading || !name.trim() || !password.trim() || !confirmPassword.trim()}
                className="w-full py-3.5 bg-[#00687a] hover:bg-[#004e5c] text-white text-sm font-bold rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>Creating Account...</span>
                  </>
                ) : (
                  <>
                    <span>Create Account</span>
                    <span className="material-symbols-outlined text-[18px]">person_add</span>
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
        Protected with PBKDF2 cryptography • SkillBridge Verifiable Credential Protocol
      </p>
    </div>
  );
};
