import React, { useState } from 'react';
import { TeamCandidate, ScreenType } from '../types';
import { CircularProgress } from '../components/common/CircularProgress';

interface TeamBuilderViewProps {
  studentName?: string;
  candidates: TeamCandidate[];
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  onInviteCandidate: (candidateId: string) => void;
  onOpenMatchModal: (candidate: TeamCandidate) => void;
  onNavigate: (screen: ScreenType) => void;
}

export const TeamBuilderView: React.FC<TeamBuilderViewProps> = ({
  studentName = 'Student',
  candidates,
  isLoading = false,
  error = null,
  onRetry,
  onInviteCandidate,
  onOpenMatchModal,
}) => {
  const [activeRoleFilter, setActiveRoleFilter] = useState<string>('All');
  const selectedProject = 'AI & UX Research Project';

  const roles = [
    { name: 'All', icon: 'apps' },
    { name: 'ML Engineer', icon: 'engineering' },
    { name: 'UI Developer', icon: 'design_services' },
    { name: 'Backend Engineer', icon: 'terminal' },
  ];

  const filteredCandidates = candidates.filter((c) => {
    if (activeRoleFilter === 'All') return true;
    if (activeRoleFilter === 'ML Engineer') return c.role.toLowerCase().includes('ml') || c.role.toLowerCase().includes('ai') || c.verifiedSkills.some(s => s.toLowerCase().includes('machine learning'));
    if (activeRoleFilter === 'UI Developer') return c.role.toLowerCase().includes('ui') || c.role.toLowerCase().includes('frontend') || c.verifiedSkills.some(s => s.toLowerCase().includes('react'));
    if (activeRoleFilter === 'Backend Engineer') return c.role.toLowerCase().includes('backend') || c.verifiedSkills.some(s => s.toLowerCase().includes('python') || s.toLowerCase().includes('fastapi'));
    return true;
  });

  const invitedCount = candidates.filter((c) => c.invited).length;
  const currentMembersCount = 1 + invitedCount; // Lead (Alex Rivera) + invited members
  const capabilityScore = Math.min(100, 65 + invitedCount * 17);

  if (isLoading) {
    return (
      <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-16 flex flex-col items-center justify-center min-h-[60vh] gap-4 font-['Inter']">
        <CircularProgress percentage={75} size={56} strokeWidth={4.5} color="#00687a" />
        <p className="text-sm font-semibold text-slate-600">Calculating explainable candidate recommendations from SQLite database...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-16 flex flex-col items-center justify-center min-h-[60vh] gap-4 font-['Inter']">
        <div className="w-16 h-16 rounded-full bg-red-50 text-red-600 flex items-center justify-center border border-red-200">
          <span className="material-symbols-outlined text-3xl">error</span>
        </div>
        <h2 className="text-xl font-bold text-slate-900">Failed to Load Team Candidates</h2>
        <p className="text-sm text-slate-600 text-center max-w-md">{error}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 px-6 py-2 bg-[#00687a] text-white text-xs font-bold rounded-full hover:bg-[#004e5c] transition-colors"
          >
            Retry Connection
          </button>
        )}
      </main>
    );
  }

  return (
    <main className="max-w-[1280px] mx-auto px-4 py-6 md:px-8 md:py-10 pb-24 md:pb-12 min-h-screen font-['Inter']">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Main Content Column */}
        <div className="md:col-span-8 flex flex-col gap-6">
          {/* Header Card */}
          <section className="bg-white border border-slate-200 rounded-2xl p-6 flex flex-col gap-3 shadow-xs relative overflow-hidden">
            <div className="absolute top-0 right-0 w-40 h-40 bg-cyan-100/40 opacity-70 rounded-bl-full pointer-events-none"></div>

            <header>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-cyan-50 text-[#00687a] border border-cyan-200">
                  Multidisciplinary Matching Engine
                </span>
              </div>
              <h1 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl font-bold text-[#191c1e] mb-1">
                Build Your Project Team
              </h1>
              <p className="text-sm text-slate-600">
                Finding optimal candidate matches for: <strong className="text-slate-900 font-semibold">{selectedProject}</strong>
              </p>
            </header>

            {/* Required Roles Pipeline */}
            <div className="pt-4 border-t border-slate-100 mt-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-3">
                REQUIRED SKILLS & ROLES PIPELINE
              </span>
              <div className="flex gap-2 overflow-x-auto hide-scrollbar pb-1">
                {roles.map((role) => {
                  const isActive = activeRoleFilter === role.name;
                  return (
                    <button
                      key={role.name}
                      onClick={() => setActiveRoleFilter(role.name)}
                      className={`shrink-0 px-4 py-2 rounded-full text-xs font-semibold flex items-center gap-2 transition-all ${
                        isActive
                          ? 'bg-[#dae2fd] text-[#131b2e] border border-[#bec6e0] shadow-2xs font-bold'
                          : 'bg-slate-50 text-slate-700 border border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[18px]">{role.icon}</span>
                      {role.name}
                    </button>
                  );
                })}
              </div>
            </div>
          </section>

          {/* Suggested Candidates Header */}
          <section className="flex flex-col gap-4">
            <div className="flex justify-between items-end">
              <h2 className="font-['Hanken_Grotesk'] text-xl sm:text-2xl font-bold text-[#191c1e]">
                Explainable Candidate Recommendations
              </h2>
              <span className="text-xs font-semibold text-slate-500">
                {filteredCandidates.length} Real Matches Found
              </span>
            </div>

            {/* Candidate Cards List */}
            {filteredCandidates.length === 0 ? (
              <div className="bg-white rounded-2xl border border-dashed border-slate-300 p-12 text-center">
                <span className="material-symbols-outlined text-slate-400 text-5xl mb-2">person_off</span>
                <h3 className="text-lg font-bold text-slate-800">No matching candidates found</h3>
                <p className="text-sm text-slate-500 mt-1">No candidate students currently match this role filter.</p>
                <button
                  onClick={() => setActiveRoleFilter('All')}
                  className="mt-4 px-4 py-2 bg-[#00687a] text-white text-xs font-bold rounded-lg"
                >
                  Show All Candidates
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredCandidates.map((candidate) => (
                  <article
                    key={candidate.id}
                    className="bg-white border border-slate-200 rounded-2xl p-6 flex flex-col gap-4 hover:shadow-md transition-all duration-200"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-4">
                        <img
                          src={candidate.avatar}
                          alt={candidate.name}
                          className="w-14 h-14 rounded-full object-cover border border-slate-200 shadow-2xs"
                        />
                        <div>
                          <h3 className="font-['Hanken_Grotesk'] text-lg font-bold text-slate-900 flex items-center gap-1.5">
                            {candidate.name}
                            <span className="material-symbols-outlined text-[#00687a] text-[18px] material-symbols-fill" title="Verified Skill Passport">
                              verified
                            </span>
                          </h3>
                          <p className="text-xs text-slate-500">
                            {candidate.role} • {candidate.level}
                          </p>
                          <p className="text-[11px] text-slate-400 mt-0.5">{candidate.education}</p>
                        </div>
                      </div>

                      {/* Match Ring Indicator */}
                      <div 
                        onClick={() => onOpenMatchModal(candidate)}
                        className="flex flex-col items-center cursor-pointer hover:scale-105 transition-transform"
                        title="View detailed AI match analysis"
                      >
                        <CircularProgress
                          percentage={candidate.matchPercentage}
                          size={52}
                          strokeWidth={4}
                          color="#00687a"
                          fontSize="text-xs font-bold"
                        />
                        <span className="text-[10px] font-bold text-[#00687a] mt-0.5">Match</span>
                      </div>
                    </div>

                    {/* AI Reasoning Block */}
                    <div className="bg-[#e9ddff] text-[#23005c] rounded-xl p-3.5 border border-[#d0bcff] flex gap-3 items-start relative overflow-hidden group">
                      <span className="material-symbols-outlined text-[#6d3bd7] text-[20px] material-symbols-fill shrink-0 mt-0.5">
                        auto_awesome
                      </span>
                      <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider block mb-0.5 text-[#6d3bd7]">
                          MATCH EXPLAINABILITY INSIGHT
                        </span>
                        <p className="text-xs text-slate-800 leading-snug">
                          {candidate.aiInsight}
                        </p>
                      </div>
                    </div>

                    {/* Top Verified Skills */}
                    <div>
                      <span className="text-[11px] font-bold uppercase text-slate-400 mb-2 block tracking-wider">
                        CONTRIBUTED VERIFIED SKILLS
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {candidate.verifiedSkills.length > 0 ? (
                          candidate.verifiedSkills.map((skill, idx) => (
                            <div
                              key={idx}
                              className="bg-[#f2f4f6] px-3 py-1.5 rounded-lg flex items-center gap-1.5 border border-slate-200 text-xs font-medium text-slate-800"
                            >
                              <span className="material-symbols-outlined text-[#00687a] text-[16px]">
                                check_circle
                              </span>
                              <span>{skill}</span>
                            </div>
                          ))
                        ) : (
                          <span className="text-xs text-slate-400 italic">General technical competency</span>
                        )}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2 pt-2">
                      <button
                        onClick={() => onOpenMatchModal(candidate)}
                        className="px-4 py-2.5 rounded-full border border-slate-200 text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors"
                      >
                        View Profile & Match
                      </button>
                      <button
                        onClick={() => onInviteCandidate(candidate.id)}
                        disabled={candidate.invited}
                        className={`flex-1 py-2.5 rounded-full font-bold text-xs transition-all flex items-center justify-center gap-2 shadow-xs ${
                          candidate.invited
                            ? 'bg-emerald-600 text-white cursor-default'
                            : 'bg-[#00687a] hover:bg-[#004e5c] text-white'
                        }`}
                      >
                        <span className="material-symbols-outlined text-[18px]">
                          {candidate.invited ? 'check' : 'person_add'}
                        </span>
                        <span>{candidate.invited ? 'Invited to Team ✓' : 'Invite to Team'}</span>
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Right Column / Team Composition Sidebar */}
        <aside className="md:col-span-4 flex flex-col gap-6">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs sticky top-20">
            <h3 className="font-['Hanken_Grotesk'] text-lg font-bold text-slate-900 border-b border-slate-100 pb-3 mb-4 flex items-center justify-between">
              <span>Team Composition</span>
              <span className="text-xs px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded font-bold">SQLite Live</span>
            </h3>

            <div className="space-y-4">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500 font-medium">Team Size Goal</span>
                <span className="font-bold text-slate-900">3-4 Members</span>
              </div>

              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500 font-medium">Active & Invited</span>
                <span className="font-bold text-[#00687a]">{currentMembersCount} Members</span>
              </div>

              {/* Capability Progress Bar */}
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-500 font-medium">Capability Score</span>
                  <span className="font-bold text-slate-800">{capabilityScore}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#00687a] h-full rounded-full transition-all duration-500"
                    style={{ width: `${capabilityScore}%` }}
                  ></div>
                </div>
              </div>

              {/* Members List */}
              <div className="pt-3 border-t border-slate-100 space-y-2.5">
                <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider block">
                  Current Roster
                </span>
                
                {/* Team Owner */}
                <div className="flex items-center gap-2.5 text-xs bg-slate-50 p-2 rounded-lg border border-slate-200">
                  <div className="w-7 h-7 rounded-full bg-[#dae2fd] text-[#131b2e] flex items-center justify-center font-bold text-[10px]">
                    {studentName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'ST'}
                  </div>
                  <div className="flex-1">
                    <p className="font-bold text-slate-800">{studentName} (You)</p>
                    <p className="text-[10px] text-slate-500">Team Creator • Lead</p>
                  </div>
                  <span className="text-[10px] font-bold text-[#00687a]">Owner</span>
                </div>

                {/* Invited candidates */}
                {candidates.filter(c => c.invited).map(c => (
                  <div key={c.id} className="flex items-center gap-2.5 text-xs bg-emerald-50/60 p-2 rounded-lg border border-emerald-200">
                    <img src={c.avatar} alt={c.name} className="w-7 h-7 rounded-full object-cover" />
                    <div className="flex-1">
                      <p className="font-bold text-slate-800">{c.name}</p>
                      <p className="text-[10px] text-slate-500">{c.role}</p>
                    </div>
                    <span className="text-[10px] font-bold text-emerald-700">Invited</span>
                  </div>
                ))}
              </div>

              <p className="text-xs text-slate-500 mt-4 pt-4 border-t border-slate-100 leading-relaxed">
                Candidates are evaluated using verified skill passport records and skill complementarity algorithms. Protected personal attributes are strictly excluded from ranking.
              </p>
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
};
