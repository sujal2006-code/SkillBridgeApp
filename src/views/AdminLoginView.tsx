import React, { useState } from 'react';
import { adminApi } from '../api';
import { ScreenType } from '../types';

interface AdminLoginViewProps {
  onLoginSuccess: () => void;
  onNavigate: (screen: ScreenType) => void;
}

export const AdminLoginView: React.FC<AdminLoginViewProps> = ({
  onLoginSuccess,
  onNavigate,
}) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!username.trim() || !password.trim()) {
      setError('Please enter both admin username and password.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await adminApi.login(username.trim(), password.trim());
      localStorage.setItem('skillbridge_admin_token', res.token);
      setIsLoading(false);
      onLoginSuccess();
    } catch (err: any) {
      setIsLoading(false);
      setError(err.message || 'Invalid admin credentials. Please try again.');
    }
  };

  return (
    <main className="min-h-[80vh] flex items-center justify-center p-4 md:p-8 font-['Inter']">
      <div className="max-w-md w-full bg-white rounded-3xl border border-slate-200 shadow-xl p-8 relative overflow-hidden">
        {/* Subtle Top Accent */}
        <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-purple-600 to-[#00687a]"></div>

        {/* Lock / Shield Icon */}
        <div className="w-14 h-14 rounded-2xl bg-purple-50 text-purple-700 flex items-center justify-center border border-purple-200 shadow-xs mb-6 mt-2">
          <span className="material-symbols-outlined text-3xl material-symbols-fill">admin_panel_settings</span>
        </div>

        <h1 className="font-['Hanken_Grotesk'] text-2xl font-bold text-slate-900 tracking-tight mb-1">
          Faculty & Admin Portal
        </h1>
        <p className="text-xs text-slate-500 mb-6">
          Authorized verification access for artifact evaluation and skill governance.
        </p>

        {error && (
          <div className="mb-5 p-3.5 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs font-semibold flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">error</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Admin Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                if (error) setError(null);
              }}
              placeholder="e.g. Sujal"
              disabled={isLoading}
              className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:bg-white transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Admin Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (error) setError(null);
              }}
              placeholder="••••••••"
              disabled={isLoading}
              className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:bg-white transition-all"
            />
          </div>

          <div className="pt-2 flex flex-col gap-3">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-purple-700 hover:bg-purple-800 text-white text-xs font-bold rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <span className="inline-block w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[18px]">lock_open</span>
                  <span>Login to Admin Portal</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => onNavigate('dashboard')}
              className="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition-colors"
            >
              Return to Student Dashboard
            </button>
          </div>
        </form>
      </div>
    </main>
  );
};
