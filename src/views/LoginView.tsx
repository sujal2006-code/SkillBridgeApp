import React, { useState, useMemo } from 'react';
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

  // Live Password Validation Checks
  const passwordCriteria = useMemo(() => {
    const hasLength = password.length >= 5;
    const hasLetter = /[a-zA-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const isAllSatisfied = hasLength && hasLetter && hasNumber;
    return { hasLength, hasLetter, hasNumber, isAllSatisfied };
  }, [password]);

  const passwordsMatch = useMemo(() => {
    if (!confirmPassword) return null;
    return password === confirmPassword;
  }, [password, confirmPassword]);

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

    // Check password rules on frontend
    if (!passwordCriteria.isAllSatisfied) {
      setErrorMessage('Password must have a minimum length of 5 characters and include at least 1 letter and 1 number.');
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
    setName('Aarav Sharma');
    setPassword('skillbridge2026');
    setMode('login');
    setErrorMessage(null);
    setSuccessMessage(null);
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col justify-center items-center px-4 py-10 font-['Inter'] relative overflow-hidden selection:bg-cyan-500/30 selection:text-cyan-200">
      
      {/* Dynamic Animated Ambient Background */}
      <div className="absolute top-1/4 -left-20 w-80 sm:w-96 h-80 sm:h-96 bg-cyan-600/20 rounded-full blur-[100px] pointer-events-none animate-pulse"></div>
      <div className="absolute -top-10 right-1/4 w-80 sm:w-96 h-80 sm:h-96 bg-indigo-600/20 rounded-full blur-[110px] pointer-events-none"></div>
      <div className="absolute bottom-10 right-10 w-72 sm:w-80 h-72 sm:h-80 bg-purple-600/15 rounded-full blur-[90px] pointer-events-none"></div>

      {/* Grid Overlay Texture */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none" 
        style={{ backgroundImage: 'radial-gradient(rgba(255,255,255,0.8) 1px, transparent 1px)', backgroundSize: '24px 24px' }}
      ></div>

      {/* Main Glassmorphism Authentication Card */}
      <div className="bg-slate-900/80 backdrop-blur-2xl border border-slate-800/90 shadow-[0_20px_60px_rgba(0,0,0,0.7)] rounded-3xl max-w-md w-full p-7 sm:p-9 relative z-10 transition-all duration-300 ring-1 ring-white/10">
        
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="relative mb-3.5 group">
            <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-teal-500 rounded-2xl blur-sm opacity-70 group-hover:opacity-100 transition duration-300"></div>
            <div className="relative w-13 h-13 rounded-2xl bg-gradient-to-br from-[#00687a] to-[#008da6] text-white flex items-center justify-center shadow-lg border border-cyan-400/30">
              <span className="material-symbols-outlined text-[28px] material-symbols-fill">widgets</span>
            </div>
          </div>
          
          <h1 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-1.5">
            SkillBridge
          </h1>
          <p className="text-xs sm:text-sm text-cyan-400/90 font-medium mt-1">
            Build your skills. Prove your potential.
          </p>
          <p className="text-xs text-slate-400 mt-1 max-w-xs leading-relaxed">
            {mode === 'login'
              ? 'Enter your credentials to continue your SkillBridge journey.'
              : 'Create your account to build your verified skill passport.'}
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex bg-slate-950/70 p-1.5 rounded-2xl mb-6 border border-slate-800/80">
          <button
            type="button"
            onClick={() => switchMode('login')}
            className={`flex-1 py-2.5 text-xs font-bold rounded-xl transition-all duration-200 cursor-pointer flex items-center justify-center gap-1.5 ${
              mode === 'login'
                ? 'bg-gradient-to-r from-cyan-600 to-[#00687a] text-white shadow-md shadow-cyan-950/50'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            id="tab-login"
          >
            <span className="material-symbols-outlined text-[16px]">login</span>
            <span>Sign In</span>
          </button>
          <button
            type="button"
            onClick={() => switchMode('register')}
            className={`flex-1 py-2.5 text-xs font-bold rounded-xl transition-all duration-200 cursor-pointer flex items-center justify-center gap-1.5 ${
              mode === 'register'
                ? 'bg-gradient-to-r from-cyan-600 to-[#00687a] text-white shadow-md shadow-cyan-950/50'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            id="tab-register"
          >
            <span className="material-symbols-outlined text-[16px]">person_add</span>
            <span>Create Account</span>
          </button>
        </div>

        {/* Success Alert */}
        {successMessage && (
          <div
            id="auth-success-alert"
            className="mb-5 p-3.5 bg-emerald-950/60 border border-emerald-500/40 rounded-xl text-emerald-300 text-xs font-medium flex items-start gap-2.5 animate-fadeIn backdrop-blur-sm"
          >
            <span className="material-symbols-outlined text-[18px] text-emerald-400 shrink-0 mt-0.5">
              check_circle
            </span>
            <span className="leading-snug">{successMessage}</span>
          </div>
        )}

        {/* Error / Validation Notification */}
        {errorMessage && (
          <div
            id="auth-error-alert"
            className="mb-5 p-3.5 bg-red-950/60 border border-red-500/40 rounded-xl text-red-300 text-xs font-medium flex flex-col gap-1.5 animate-fadeIn backdrop-blur-sm"
          >
            <div className="flex items-start gap-2.5">
              <span className="material-symbols-outlined text-[18px] text-red-400 shrink-0 mt-0.5">
                error
              </span>
              <span className="leading-snug">{errorMessage}</span>
            </div>
            {errorMessage.toLowerCase().includes('already exists') && mode === 'register' && (
              <button
                type="button"
                onClick={() => switchMode('login')}
                className="self-start ml-7 text-xs font-bold text-cyan-400 hover:text-cyan-300 hover:underline cursor-pointer flex items-center gap-1 mt-0.5"
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
              <label htmlFor="login-name-input" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Name
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
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
                  placeholder="Enter your registered name"
                  disabled={isLoading}
                  autoFocus
                  required
                  className="w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-800 rounded-xl text-sm font-medium text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                />
              </div>
            </div>

            <div>
              <label htmlFor="login-password-input" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
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
                  className="w-full pl-10 pr-11 py-3 bg-slate-950/70 border border-slate-800 rounded-xl text-sm font-medium text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-200 focus:outline-none cursor-pointer"
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
                className="w-full py-3.5 bg-gradient-to-r from-cyan-600 via-[#00687a] to-teal-600 hover:brightness-110 text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-cyan-950/60 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer active:scale-[0.99]"
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

            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => switchMode('register')}
                className="text-xs text-slate-400 hover:text-cyan-300 font-medium transition-colors cursor-pointer"
              >
                Don't have an account? <span className="text-cyan-400 font-bold underline">Create an account</span>
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
              <label htmlFor="reg-name-input" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Name
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
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
                  className="w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-800 rounded-xl text-sm font-medium text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                />
              </div>
            </div>

            <div>
              <label htmlFor="reg-password-input" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
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
                  placeholder="At least 5 chars with letters & numbers"
                  disabled={isLoading}
                  required
                  className="w-full pl-10 pr-11 py-3 bg-slate-950/70 border border-slate-800 rounded-xl text-sm font-medium text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-200 focus:outline-none cursor-pointer"
                  tabIndex={-1}
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>

              {/* Live Password Requirements Checklist */}
              <div className="mt-2.5 bg-slate-950/50 p-2.5 rounded-xl border border-slate-800/80 space-y-1.5 text-[11px]">
                <p className="text-slate-400 font-semibold mb-1">Password requirements:</p>
                <div className={`flex items-center gap-1.5 transition-colors ${passwordCriteria.hasLength ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                  <span className="material-symbols-outlined text-[14px]">
                    {passwordCriteria.hasLength ? 'check_circle' : 'radio_button_unchecked'}
                  </span>
                  <span>Minimum 5 characters</span>
                </div>
                <div className={`flex items-center gap-1.5 transition-colors ${passwordCriteria.hasLetter ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                  <span className="material-symbols-outlined text-[14px]">
                    {passwordCriteria.hasLetter ? 'check_circle' : 'radio_button_unchecked'}
                  </span>
                  <span>Contains at least 1 letter (A-Z or a-z)</span>
                </div>
                <div className={`flex items-center gap-1.5 transition-colors ${passwordCriteria.hasNumber ? 'text-emerald-400 font-medium' : 'text-slate-500'}`}>
                  <span className="material-symbols-outlined text-[14px]">
                    {passwordCriteria.hasNumber ? 'check_circle' : 'radio_button_unchecked'}
                  </span>
                  <span>Contains at least 1 number (0-9)</span>
                </div>
              </div>
            </div>

            <div>
              <label htmlFor="reg-confirm-password-input" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Confirm Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
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
                  className={`w-full pl-10 pr-11 py-3 bg-slate-950/70 border rounded-xl text-sm font-medium text-white placeholder:text-slate-500 focus:outline-none transition-all ${
                    passwordsMatch === false && confirmPassword.length > 0
                      ? 'border-red-500/80 focus:ring-2 focus:ring-red-500/20'
                      : passwordsMatch === true
                      ? 'border-emerald-500/80 focus:ring-2 focus:ring-emerald-500/20'
                      : 'border-slate-800 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-200 focus:outline-none cursor-pointer"
                  tabIndex={-1}
                  title={showConfirmPassword ? 'Hide password' : 'Show password'}
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showConfirmPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
              {confirmPassword.length > 0 && (
                <p className={`text-[11px] mt-1.5 flex items-center gap-1 font-medium ${passwordsMatch ? 'text-emerald-400' : 'text-red-400'}`}>
                  <span className="material-symbols-outlined text-[13px]">
                    {passwordsMatch ? 'check_circle' : 'cancel'}
                  </span>
                  <span>{passwordsMatch ? 'Passwords match' : 'Passwords do not match'}</span>
                </p>
              )}
            </div>

            <div className="pt-2">
              <button
                id="register-submit-button"
                type="submit"
                disabled={isLoading || !name.trim() || !password.trim() || !confirmPassword.trim()}
                className="w-full py-3.5 bg-gradient-to-r from-cyan-600 via-[#00687a] to-teal-600 hover:brightness-110 text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-cyan-950/60 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer active:scale-[0.99]"
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

            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => switchMode('login')}
                className="text-xs text-slate-400 hover:text-cyan-300 font-medium transition-colors cursor-pointer"
              >
                Already have an account? <span className="text-cyan-400 font-bold underline">Sign In</span>
              </button>
            </div>
          </form>
        )}

        {/* Demo Fast-Fill Helper for Testing (Only on Login) */}
        {mode === 'login' && (
          <div className="mt-6 pt-5 border-t border-slate-800/80 flex flex-col items-center">
            <p className="text-[11px] text-slate-500 text-center mb-1.5">
              Need a quick demo profile?
            </p>
            <button
              type="button"
              onClick={handleQuickFillDemo}
              className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 hover:underline flex items-center gap-1 cursor-pointer transition-colors"
            >
              <span className="material-symbols-outlined text-[14px]">bolt</span>
              <span>Use Demo Profile (Aarav Sharma)</span>
            </button>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <p className="text-xs text-slate-500 text-center mt-6">
        Protected with PBKDF2 cryptography • SkillBridge Verifiable Credential Protocol
      </p>
    </div>
  );
};
