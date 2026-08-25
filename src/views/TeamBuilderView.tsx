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
  const selectedProject = 'AI & UX Research Platform';

  const roles = [
    { name: 'All', icon: 'apps' },
    { name: 'ML & AI', icon: 'psychology' },
    { name: 'Frontend & UI', icon: 'design_services' },
    { name: 'Backend', icon: 'terminal' },
    { name: 'Data Systems', icon: 'database' },
    { name: 'DevOps & Cloud', icon: 'cloud' },
  ];

  const filteredCandidates = candidates.filter((c) => {
    if (activeRoleFilter === 'All') return true;
    if (activeRoleFilter === 'ML & AI') {
      return (
        c.role.toLowerCase().includes('ml') ||
        c.role.toLowerCase().includes('ai') ||
        c.verifiedSkills.some((s) => s.toLowerCase().includes('machine learning') || s.toLowerCase().includes('python'))
      );
    }
    if (activeRoleFilter === 'Frontend & UI') {
      return (
        c.role.toLowerCase().includes('ui') ||
        c.role.toLowerCase().includes('frontend') ||
        c.verifiedSkills.some((s) => s.toLowerCase().includes('react') || s.toLowerCase().includes('javascript') || s.toLowerCase().includes('css'))
      );
    }
    if (activeRoleFilter === 'Backend') {
      return (
        c.role.toLowerCase().includes('backend') ||
        c.verifiedSkills.some((s) => s.toLowerCase().includes('fastapi') || s.toLowerCase().includes('spring') || s.toLowerCase().includes('java'))
      );
    }
    if (activeRoleFilter === 'Data Systems') {
      return (
        c.role.toLowerCase().includes('data') ||
        c.verifiedSkills.some((s) => s.toLowerCase().includes('sql') || s.toLowerCase().includes('database') || s.toLowerCase().includes('pandas'))
      );
    }
    if (activeRoleFilter === 'DevOps & Cloud') {
      return (
        c.role.toLowerCase().includes('devops') ||
        c.role.toLowerCase().includes('cloud') ||
        c.verifiedSkills.some((s) => s.toLowerCase().includes('docker') || s.toLowerCase().includes('git') || s.toLowerCase().includes('aws'))
      );
    }
    return true;
  });

  const invitedCount = candidates.filter((c) => c.invited).length;
  const currentMembersCount = 1 + invitedCount;
  const capabilityScore = Math.min(100, 65 + invitedCount * 17);

  if (isLoading) {
    return (
      <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-16 flex flex-col items-center justify-center min-h-[60vh] gap-4 font-['Inter']">
        <CircularProgress percentage={75} size={56} strokeWidth={4.5} color="#00687a" />
        <p className="text-sm font-semibold text-slate-600">
          Evaluating team gaps and candidate skill complementarity from Neon PostgreSQL...
        </p>
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
                  Fair Complementarity Engine
                </span>
              </div>
              <h1 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl font-bold text-[#191c1e] mb-1">
                Build Your Project Team
              </h1>
              <p className="text-sm text-slate-600">
                Finding complementary candidates for: <strong className="text-slate-900 font-semibold">{selectedProject}</strong>
              </p>
            </header>

            {/* Required Roles Pipeline */}
            <div className="pt-4 border-t border-slate-100 mt-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-3">
                EXPLORE BY DOMAIN & CAPABILITY
              </span>
              <div className="flex gap-2 overflow-x-auto hide-scrollbar pb-1">
                {roles.map((role) => {
                  const isActive = activeRoleFilter === role.name;
                  return (
                    <button
                      key={role.name}
                      onClick={() => setActiveRoleFilter(role.name)}
                      className={`shrink-0 px-4 py-2 rounded-full text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer ${
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
              <div>
                <h2 className="font-['Hanken_Grotesk'] text-xl sm:text-2xl font-bold text-[#191c1e]">
                  Explainable Candidate Matches
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Ranked by team gap fulfillment and complementary capability coverage.
                </p>
              </div>
              <span className="text-xs font-semibold text-slate-500 shrink-0">
                {filteredCandidates.length} Candidates Available
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
                  className="mt-4 px-4 py-2 bg-[#00687a] text-white text-xs font-bold rounded-lg cursor-pointer"
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
                          <p className="text-xs text-slate-500 font-medium">
                            {candidate.role} • {candidate.level}
                          </p>
                          <p className="text-[11px] text-slate-400 mt-0.5">{candidate.education}</p>
                        </div>
                      </div>

                      {/* Match Ring Indicator */}
                      <div 
                        onClick={() => onOpenMatchModal(candidate)}
                        className="flex flex-col items-center cursor-pointer hover:scale-105 transition-transform"
                        title="View explainable matching breakdown"
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

                    {/* AI Explainability Box */}
                    <div className="bg-[#e9ddff]/70 text-[#23005c] rounded-xl p-3.5 border border-[#d0bcff] flex gap-3 items-start relative overflow-hidden group">
                      <span className="material-symbols-outlined text-[#6d3bd7] text-[20px] material-symbols-fill shrink-0 mt-0.5">
                        auto_awesome
                      </span>
                      <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider block mb-0.5 text-[#6d3bd7]">
                          WHY RECOMMENDED FOR THIS TEAM
                        </span>
                        <p className="text-xs text-slate-800 leading-snug">
                          {candidate.aiInsight}
                        </p>
                      </div>
                    </div>

                    {/* Contributed, Missing & Complementary Skills */}
                    <div className="flex flex-col gap-2.5">
                      {candidate.skillsContributed && candidate.skillsContributed.length > 0 && (
                        <div>
                          <span className="text-[11px] font-bold uppercase text-slate-400 mb-1.5 block tracking-wider">
                            ✓ Fills Team Skill Gaps
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {candidate.skillsContributed.map((skill, idx) => (
                              <span
                                key={idx}
                                className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1"
                              >
                                <span className="material-symbols-outlined text-[14px] text-emerald-600">check_circle</span>
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {candidate.missingSkills && candidate.missingSkills.length > 0 && (
                        <div>
                          <span className="text-[11px] font-bold uppercase text-amber-800/80 mb-1.5 block tracking-wider">
                            • Missing Skills
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {candidate.missingSkills.map((skill, idx) => (
                              <span
                                key={idx}
                                className="bg-amber-50/80 text-amber-900 border border-amber-200/80 px-2.5 py-1 rounded-lg text-xs font-medium flex items-center gap-1"
                              >
                                <span className="material-symbols-outlined text-[14px] text-amber-600">close</span>
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {candidate.complementarySkills && candidate.complementarySkills.length > 0 && (
                        <div>
                          <span className="text-[11px] font-bold uppercase text-slate-400 mb-1.5 block tracking-wider">
                            + Adds Complementary Domain Breadth
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {candidate.complementarySkills.map((skill, idx) => (
                              <span
                                key={idx}
                                className="bg-cyan-50 text-[#004e5c] border border-cyan-200 px-2.5 py-1 rounded-lg text-xs font-medium flex items-center gap-1"
                              >
                                <span className="material-symbols-outlined text-[14px] text-[#00687a]">extension</span>
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2 pt-2 border-t border-slate-100 items-center justify-between">
                      <button
                        onClick={() => onOpenMatchModal(candidate)}
                        className="px-4 py-2 rounded-full border border-slate-200 text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors cursor-pointer"
                      >
                        View Full Match Breakdown
                      </button>
                      <button
                        onClick={() => onInviteCandidate(candidate.id)}
                        disabled={candidate.invited}
                        className={`px-6 py-2.5 rounded-full font-bold text-xs transition-all flex items-center justify-center gap-2 shadow-xs cursor-pointer ${
                          candidate.invited
                            ? 'bg-emerald-600 text-white cursor-default'
                            : 'bg-[#00687a] hover:bg-[#004e5c] text-white'
                        }`}
                      >
                        <span className="material-symbols-outlined text-[18px]">
                          {candidate.invited ? 'check' : 'person_add'}
                        </span>
                        <span>{candidate.invited ? 'Invitation Sent ✓' : 'Send Team Invitation'}</span>
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
              <span className="text-xs px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded font-bold">
                Neon DB Live
              </span>
            </h3>

            <div className="space-y-4">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500 font-medium">Team Size Rule</span>
                <span className="font-bold text-slate-900">Min 2, Max 6 Members</span>
              </div>

              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500 font-medium">Active Members & Invites</span>
                <span className="font-bold text-[#00687a]">{currentMembersCount} of 6 Members</span>
              </div>

              {/* Capability Progress Bar */}
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-500 font-medium">Skill Coverage Index</span>
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
                <div className="flex items-center gap-2.5 text-xs bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                  <div className="w-8 h-8 rounded-full bg-[#dae2fd] text-[#131b2e] flex items-center justify-center font-bold text-xs shrink-0">
                    {studentName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'ST'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-slate-800 truncate">{studentName} (You)</p>
                    <p className="text-[10px] text-slate-500">Team Creator & Lead</p>
                  </div>
                  <span className="text-[10px] font-bold text-[#00687a] px-2 py-0.5 bg-cyan-50 border border-cyan-200 rounded-full">
                    Lead
                  </span>
                </div>

                {/* Invited candidates */}
                {candidates.filter(c => c.invited).map(c => (
                  <div key={c.id} className="flex items-center gap-2.5 text-xs bg-emerald-50/60 p-2.5 rounded-xl border border-emerald-200">
                    <img src={c.avatar} alt={c.name} className="w-8 h-8 rounded-full object-cover shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="font-bold text-slate-800 truncate">{c.name}</p>
                      <p className="text-[10px] text-slate-500 truncate">{c.role}</p>
                    </div>
                    <span className="text-[10px] font-bold text-emerald-700 px-2 py-0.5 bg-emerald-100 rounded-full">
                      Invited
                    </span>
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-4 border-t border-slate-100 flex items-start gap-2 text-slate-500 text-[11px] leading-relaxed">
                <span className="material-symbols-outlined text-slate-400 text-sm shrink-0 mt-0.5">verified_user</span>
                <p>
                  Fairness Guarantee: Evaluated strictly on verified skill passports and technical domain complementarity. Demographic and protected attributes are excluded.
                </p>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
};
