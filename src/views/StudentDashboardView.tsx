import React from 'react';
import { Internship, ActivityItem, ScreenType } from '../types';
import { CircularProgress } from '../components/common/CircularProgress';

interface StudentDashboardProps {
  studentName?: string;
  internships: Internship[];
  activities: ActivityItem[];
  verifiedSkillsCount: number;
  evidenceItemsCount: number;
  pendingEvidenceCount?: number;
  verifiedEvidenceCount?: number;
  teamMatchesCount?: number;
  completionPercentage?: number;
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  onNavigate: (screen: ScreenType) => void;
  onSelectInternship: (internship: Internship) => void;
}

export const StudentDashboardView: React.FC<StudentDashboardProps> = ({
  studentName = 'Alex Rivera',
  internships,
  activities,
  verifiedSkillsCount,
  evidenceItemsCount,
  pendingEvidenceCount = 0,
  verifiedEvidenceCount = 0,
  teamMatchesCount = 0,
  completionPercentage = 0,
  isLoading = false,
  error = null,
  onRetry,
  onNavigate,
  onSelectInternship,
}) => {
  const firstName = studentName.split(' ')[0] || 'Student';

  // Dynamic formula: 0 skills = 0%, 1 = 20%, 2 = 40%, 3 = 60%, 4 = 80%, 5+ = 100%
  const dynamicCompletion = typeof completionPercentage === 'number' 
    ? completionPercentage 
    : Math.min(100, verifiedSkillsCount * 20);

  if (isLoading) {
    return (
      <main className="max-w-[1280px] mx-auto p-4 md:p-8 flex flex-col items-center justify-center min-h-[60vh] gap-4 font-['Inter']">
        <CircularProgress percentage={75} size={56} strokeWidth={4.5} color="#00687a" />
        <p className="text-sm font-semibold text-slate-600">Loading student passport & live recommendations...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="max-w-[1280px] mx-auto p-4 md:p-8 flex flex-col items-center justify-center min-h-[60vh] gap-4 font-['Inter']">
        <div className="w-16 h-16 rounded-full bg-red-50 text-red-600 flex items-center justify-center border border-red-200">
          <span className="material-symbols-outlined text-3xl">error</span>
        </div>
        <h2 className="text-xl font-bold text-slate-900">Failed to Load Dashboard Data</h2>
        <p className="text-sm text-slate-600 max-w-md text-center">{error}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 px-6 py-2.5 bg-[#00687a] text-white text-xs font-bold rounded-full hover:bg-[#004e5c] transition-colors shadow-xs flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-[16px]">refresh</span>
            <span>Retry Connection</span>
          </button>
        )}
      </main>
    );
  }

  return (
    <main className="max-w-[1280px] mx-auto p-4 md:p-8 flex flex-col gap-6 md:gap-8 pb-24 md:pb-12 min-h-screen font-['Inter']">
      {/* Greeting Header */}
      <section className="mt-1 md:mt-2">
        <h1 className="font-['Hanken_Grotesk'] text-3xl sm:text-4xl md:text-[44px] font-bold text-[#191c1e] tracking-tight">
          Hi, {firstName}!
        </h1>
        <p className="text-base sm:text-lg text-slate-600 mt-1">
          Here is your verified skill passport progress and live explainable matching insights.
        </p>
      </section>

      {/* Bento Grid: Passport Completion & Key Stats */}
      <section className="grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-6">
        {/* Passport Completion Card (Spans 8 cols on desktop) */}
        <div 
          onClick={() => onNavigate('passport')}
          className="md:col-span-8 bg-white border border-slate-200 rounded-2xl p-6 flex flex-col justify-between shadow-xs hover:shadow-md transition-shadow relative overflow-hidden group cursor-pointer"
        >
          {/* Subtle glow circle */}
          <div className="absolute -right-16 -top-16 w-64 h-64 bg-cyan-100/50 rounded-full blur-3xl group-hover:opacity-100 opacity-60 transition-opacity pointer-events-none"></div>

          <div className="flex justify-between items-start mb-8 relative z-10">
            <div>
              <h2 className="font-['Hanken_Grotesk'] text-xl sm:text-2xl font-bold text-[#191c1e]">
                Passport Completion
              </h2>
              <p className="text-sm text-slate-600 mt-1">
                Your core competencies are dynamically calculated from verified artifacts.
              </p>
            </div>
            <div className="w-10 h-10 rounded-full bg-[#f2f4f6] flex items-center justify-center text-[#00687a] border border-slate-200 shadow-2xs">
              <span className="material-symbols-outlined material-symbols-fill text-[22px]">verified</span>
            </div>
          </div>

          <div className="relative z-10">
            <div className="flex justify-between items-end mb-2">
              <span className="font-['Hanken_Grotesk'] text-4xl sm:text-5xl font-bold text-[#191c1e]">
                {dynamicCompletion}%
              </span>
              <span className="text-xs font-bold text-[#00687a]">
                {dynamicCompletion > 0 ? `${verifiedSkillsCount} Verified Skill${verifiedSkillsCount > 1 ? 's' : ''}` : 'Start Building Passport'}
              </span>
            </div>
            {/* Progress Bar */}
            <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-[#00687a] rounded-full relative overflow-hidden transition-all duration-1000"
                style={{ width: `${dynamicCompletion}%` }}
              >
                <div className="absolute inset-0 bg-white/25 w-full h-full transform -skew-x-12 animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Key Stats Grid (Spans 4 cols on desktop) */}
        <div className="md:col-span-4 grid grid-cols-2 md:grid-cols-1 gap-3 md:gap-4">
          {/* Stat 1: Verified Skills */}
          <div 
            onClick={() => onNavigate('passport')}
            className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3.5 shadow-2xs hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <div className="w-12 h-12 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0 border border-emerald-100">
              <span className="material-symbols-outlined text-[26px]">workspace_premium</span>
            </div>
            <div>
              <p className="font-['Hanken_Grotesk'] text-2xl font-bold text-slate-900 leading-none">
                {verifiedSkillsCount}
              </p>
              <p className="text-[11px] font-semibold text-slate-500 mt-1 uppercase tracking-wider">
                Verified Skills
              </p>
            </div>
          </div>

          {/* Stat 2: Evidence Summary */}
          <div 
            onClick={() => onNavigate('passport')}
            className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3.5 shadow-2xs hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <div className="w-12 h-12 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-[26px]">description</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <p className="font-['Hanken_Grotesk'] text-2xl font-bold text-slate-900 leading-none">
                  {evidenceItemsCount}
                </p>
                {pendingEvidenceCount > 0 && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 font-bold">
                    {pendingEvidenceCount} pending
                  </span>
                )}
              </div>
              <p className="text-[11px] font-semibold text-slate-500 mt-1 uppercase tracking-wider">
                Evidence Artifacts
              </p>
            </div>
          </div>

          {/* Stat 3: Internships / Opportunities */}
          <div 
            onClick={() => onNavigate('internships')}
            className="col-span-2 md:col-span-1 bg-[#06b6d4] border border-cyan-400 rounded-xl p-4 flex items-center gap-3.5 shadow-xs cursor-pointer hover:brightness-105 transition-all text-[#00424f]"
          >
            <div className="w-12 h-12 rounded-lg bg-[#00424f] text-[#06b6d4] flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-[26px]">handshake</span>
            </div>
            <div>
              <p className="font-['Hanken_Grotesk'] text-2xl font-bold text-[#00424f] leading-none">
                {internships.length} Available
              </p>
              <p className="text-[11px] font-bold text-[#00424f]/90 mt-1 uppercase tracking-wider">
                Explainable Matches
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Starter Callout for 0% / New Users */}
      {verifiedSkillsCount === 0 && (
        <section className="bg-white border-2 border-dashed border-[#00687a]/40 rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xs">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-cyan-50 text-[#00687a] flex items-center justify-center shrink-0 border border-cyan-200">
              <span className="material-symbols-outlined text-3xl">upload_file</span>
            </div>
            <div>
              <h3 className="font-['Hanken_Grotesk'] text-xl font-bold text-slate-900">
                Your Skill Passport starts here
              </h3>
              <p className="text-sm text-slate-600 mt-1 max-w-xl">
                Add coursework, projects, competitions, or micro-credentials. Once verified, each artifact builds your verified skill passport and automatically unlocks explainable internship and team matches.
              </p>
            </div>
          </div>
          <button
            onClick={() => onNavigate('add-evidence')}
            className="px-6 py-3 bg-[#00687a] hover:bg-[#004e5c] text-white font-bold text-xs rounded-full transition-all shadow-xs flex items-center gap-2 shrink-0"
          >
            <span className="material-symbols-outlined text-[18px]">add_circle</span>
            <span>Add First Evidence</span>
          </button>
        </section>
      )}

      {/* Top Recommendations Feed */}
      <section className="flex flex-col gap-4">
        <div className="flex justify-between items-end">
          <div>
            <h2 className="font-['Hanken_Grotesk'] text-2xl font-bold text-[#191c1e]">
              Top Matched Internships
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Ranked with 100% deterministic explainability based strictly on verified skills.
            </p>
          </div>
          <button 
            onClick={() => onNavigate('internships')}
            className="text-xs font-bold text-[#00687a] hover:underline flex items-center gap-0.5"
          >
            <span>View all ({internships.length})</span>
            <span className="material-symbols-outlined text-[16px]">chevron_right</span>
          </button>
        </div>

        {internships.length === 0 ? (
          <div className="bg-white rounded-2xl border border-dashed border-slate-300 p-12 text-center">
            <span className="material-symbols-outlined text-slate-400 text-5xl mb-2">work_off</span>
            <h3 className="text-lg font-bold text-slate-800">No matching internships found yet</h3>
            <p className="text-sm text-slate-500 mt-1">Add and verify your coursework or projects to generate matches.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {internships.slice(0, 3).map((internship) => (
              <div
                key={internship.id}
                onClick={() => onSelectInternship(internship)}
                className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col justify-between hover:shadow-md transition-all cursor-pointer group"
              >
                <div>
                  <div className="flex justify-between items-start mb-3">
                    <img
                      src={internship.logo}
                      alt={internship.company}
                      className="w-12 h-12 rounded-xl object-cover border border-slate-200 shadow-2xs"
                    />
                    <div className="flex flex-col items-center">
                      <CircularProgress
                        percentage={internship.matchPercentage}
                        size={48}
                        strokeWidth={4}
                        color="#00687a"
                        fontSize="text-xs font-bold"
                      />
                      <span className="text-[10px] font-bold text-[#00687a] mt-0.5">Match</span>
                    </div>
                  </div>

                  <h3 className="font-['Hanken_Grotesk'] text-base font-bold text-slate-900 group-hover:text-[#00687a] transition-colors leading-snug">
                    {internship.title}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {internship.company} • {internship.location}
                  </p>

                  <p className="text-xs text-slate-600 mt-3 line-clamp-2 leading-relaxed">
                    {internship.explanation || internship.description}
                  </p>
                </div>

                <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs text-slate-500">
                    <span className="material-symbols-outlined text-[16px] text-emerald-600">verified</span>
                    <span>{internship.verifiedSkills.length} Matched</span>
                  </div>
                  <span className="text-xs font-bold text-[#00687a] flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
                    <span>Explain Match</span>
                    <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Activity Feed */}
      <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs">
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-['Hanken_Grotesk'] text-xl font-bold text-[#191c1e]">
            Recent Activity & Audit Log
          </h2>
          <span className="text-xs font-semibold text-slate-400">Database Sync Active</span>
        </div>

        {activities.length === 0 ? (
          <p className="text-xs text-slate-400 py-4 text-center">No recent activities recorded yet.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {activities.slice(0, 5).map((act) => (
              <div key={act.id} className="py-3 flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                  <span className="material-symbols-outlined text-[18px]">{act.icon}</span>
                </div>
                <div className="flex-1">
                  <p className="text-xs font-bold text-slate-800">{act.title}</p>
                  <p className="text-[11px] text-slate-500">{act.subtitle}</p>
                </div>
                <span className="text-[10px] text-slate-400 font-medium">{act.time}</span>
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  );
};
