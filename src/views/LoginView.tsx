import React, { useState } from 'react';
import { studentsApi } from '../api';
import { ApiStudentLoginResponse } from '../types';

interface LoginViewProps {
  onLoginSuccess: (authData: ApiStudentLoginResponse) => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
  const [isRegisterMode, setIsRegisterMode] = useState<boolean>(false);
  const [name, setName] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedName = name.trim();
    const trimmedPassword = password.trim();

    if (!trimmedName || !trimmedPassword) {
      setErrorMessage('Please enter both your name and password to continue.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const mode = isRegisterMode ? 'register' : 'login';
      const response = await studentsApi.loginStudent(trimmedName, trimmedPassword, mode);
      onLoginSuccess(response);
    } catch (err: any) {
      setIsLoading(false);
      const msg = err.message || 'Authentication failed. Please check your credentials and try again.';
      setErrorMessage(msg);
    }
  };

  const handleQuickFillDemo = () => {
    setName('Alex Rivera');
    setPassword('stanford2026');
    setIsRegisterMode(false);
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-[#f7f9fb] flex flex-col justify-center items-center px-4 py-12 font-['Inter'] relative overflow-hidden">
      {/* Background Decorative Ambience */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-cyan-100/50 rounded-full blur-3xl pointer-events-none -z-10"></div>
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-purple-100/40 rounded-full blur-3xl pointer-events-none -z-10"></div>

      {/* Main Login Card */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xl max-w-md w-full p-8 sm:p-10 relative">
        {/* Brand Icon & Heading */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-[#00687a] text-white flex items-center justify-center shadow-sm mb-4">
            <span className="material-symbols-outlined text-[30px] material-symbols-fill">widgets</span>
          </div>
          <h1 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl font-bold text-[#191c1e] tracking-tight">
            SkillBridge
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1.5 max-w-xs">
            {isRegisterMode
              ? 'Create your account to start building your verified Digital Skill Passport.'
              : 'Sign in to resume your learning journey and view verified matches.'}
          </p>
        </div>

        {/* Tab Switcher (Log In / Create Account) */}
        <div className="flex bg-slate-100 p-1 rounded-xl mb-6">
          <button
            type="button"
            onClick={() => {
              setIsRegisterMode(false);
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
              !isRegisterMode
                ? 'bg-white text-[#00687a] shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            id="tab-login"
          >
            Log In
          </button>
          <button
            type="button"
            onClick={() => {
              setIsRegisterMode(true);
              setErrorMessage(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
              isRegisterMode
                ? 'bg-white text-[#00687a] shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            id="tab-register"
          >
            Create Account
          </button>
        </div>

        {/* Error / Validation Notification */}
        {errorMessage && (
          <div
            id="login-error-alert"
            className="mb-5 p-3.5 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs font-medium flex items-start gap-2.5 animate-fadeIn"
          >
            <span className="material-symbols-outlined text-[18px] text-red-600 shrink-0 mt-0.5">
              error
            </span>
            <span className="leading-snug">{errorMessage}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name Field */}
          <div>
            <label
              htmlFor="login-name-input"
              className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5"
            >
              Full Name / Identifier
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
                placeholder="e.g. Alex Rivera or Sujal"
                disabled={isLoading}
                autoFocus
                required
                className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
              />
            </div>
          </div>

          {/* Password Field */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label
                htmlFor="login-password-input"
                className="block text-xs font-bold text-slate-700 uppercase tracking-wider"
              >
                Password
              </label>
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
                placeholder="Enter your account password"
                disabled={isLoading}
                required
                className="w-full pl-10 pr-11 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none"
                tabIndex={-1}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                <span className="material-symbols-outlined text-[18px]">
                  {showPassword ? 'visibility_off' : 'visibility'}
                </span>
              </button>
            </div>
          </div>

          {/* Submit Button */}
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
                  <span>{isRegisterMode ? 'Creating Account...' : 'Signing In...'}</span>
                </>
              ) : (
                <>
                  <span>{isRegisterMode ? 'Create Passport Account' : 'Sign In & Resume'}</span>
                  <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Demo Fast-Fill Helper for Testing */}
        <div className="mt-6 pt-5 border-t border-slate-100 flex flex-col items-center">
          <p className="text-[11px] text-slate-400 text-center mb-2">
            Need a quick demo profile?
          </p>
          <button
            type="button"
            onClick={handleQuickFillDemo}
            className="text-xs font-semibold text-[#00687a] hover:text-[#004e5c] hover:underline flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-[14px]">bolt</span>
            <span>Use Demo Profile (Alex Rivera)</span>
          </button>
        </div>
      </div>

      {/* Footer Info */}
      <p className="text-xs text-slate-400 text-center mt-6">
        Protected with PBKDF2 cryptography • SkillBridge Verifiable Credential Protocol
      </p>
    </div>
  );
};
