import React, { useState } from 'react';

interface OnboardingModalProps {
  isOpen: boolean;
  onComplete: (studentName: string) => Promise<void>;
  isLoading?: boolean;
}

export const OnboardingModal: React.FC<OnboardingModalProps> = ({
  isOpen,
  onComplete,
  isLoading = false,
}) => {
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setError('Please enter your full name to proceed.');
      return;
    }
    setError(null);
    try {
      await onComplete(trimmed);
    } catch (err: any) {
      setError(err.message || 'Failed to onboard student. Please try again.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-xs animate-fadeIn font-['Inter']">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-lg w-full p-8 relative overflow-hidden">
        {/* Ambient Top Glow */}
        <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-100/60 rounded-bl-full pointer-events-none"></div>

        {/* Header Icon */}
        <div className="w-14 h-14 rounded-2xl bg-cyan-50 text-[#00687a] flex items-center justify-center border border-cyan-200 shadow-xs mb-6">
          <span className="material-symbols-outlined text-3xl material-symbols-fill">verified_user</span>
        </div>

        <h1 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight mb-2">
          Welcome to SkillBridge
        </h1>
        <p className="text-sm text-slate-600 leading-relaxed mb-6">
          Build your verified skill passport and discover explainable internship and team opportunities backed by real evidence.
        </p>

        {error && (
          <div className="mb-4 p-3.5 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs font-semibold flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">error</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label htmlFor="student-full-name" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Full Name
            </label>
            <input
              id="student-full-name"
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (error) setError(null);
              }}
              placeholder="e.g. Sujal or Aarav Sharma"
              disabled={isLoading}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00687a] focus:bg-white transition-all"
              autoFocus
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={isLoading || !name.trim()}
              className="w-full py-3.5 bg-[#00687a] hover:bg-[#004e5c] text-white text-sm font-bold rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  <span>Creating Your Passport...</span>
                </>
              ) : (
                <>
                  <span>Continue</span>
                  <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </>
              )}
            </button>
          </div>
        </form>

        <p className="text-[11px] text-slate-400 text-center mt-6">
          Your credentials are strictly evaluated against verified coursework, projects, and competitions without bias.
        </p>
      </div>
    </div>
  );
};
