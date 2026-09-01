import React, { useState, useEffect } from 'react';
import { TeamCandidate, ScreenType, ApiTeam } from '../types';
import { CircularProgress } from '../components/common/CircularProgress';
import { teamsApi } from '../api/teams';

interface TeamBuilderViewProps {
  studentName?: string;
  candidates: TeamCandidate[];
  teamId?: number;
  activeTeam?: ApiTeam | null;
  initialRoleFilter?: string;
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  onInviteCandidate: (candidateId: string) => void;
  onOpenMatchModal: (candidate: TeamCandidate) => void;
  onNavigate: (screen: ScreenType) => void;
}

const ROLE_FILTERS = [
  { name: 'All Roles', value: 'All', icon: 'apps' },
  { name: 'Frontend Developer', value: 'Frontend Developer', icon: 'desktop_windows' },
  { name: 'Backend Developer', value: 'Backend Developer', icon: 'terminal' },
  { name: 'AI/ML Developer', value: 'AI/ML Developer', icon: 'psychology' },
  { name: 'Database Specialist', value: 'Database Specialist', icon: 'database' },
  { name: 'UI/UX Designer', value: 'UI/UX Designer', icon: 'palette' },
  { name: 'DevOps Engineer', value: 'DevOps Engineer', icon: 'cloud' },
  { name: 'Full Stack Developer', value: 'Full Stack Developer', icon: 'layers' },
];

export const TeamBuilderView: React.FC<TeamBuilderViewProps> = ({
  studentName = 'Student',
  candidates: initialCandidates,
  teamId = 1,
  activeTeam = null,
  initialRoleFilter = 'All',
  isLoading = false,
  error = null,
  onRetry,
  onInviteCandidate,
  onOpenMatchModal,
  onNavigate,
}) => {
  const [activeRoleFilter, setActiveRoleFilter] = useState<string>(initialRoleFilter);
  const [candidatesList, setCandidatesList] = useState<TeamCandidate[]>(initialCandidates);
  const [isFiltering, setIsFiltering] = useState(false);

  // Sync initial candidates
  useEffect(() => {
    setCandidatesList(initialCandidates);
  }, [initialCandidates]);

  // When role filter changes, fetch role-specific recalculation from backend
  const handleFilterChange = async (filterValue: string) => {
    setActiveRoleFilter(filterValue);
    setIsFiltering(true);
    try {
      const recs = await teamsApi.getTeamCandidates(teamId, filterValue === 'All' ? undefined : filterValue);
      if (recs && recs.length > 0) {
        const AVATARS = [
          'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
          'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
          'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80',
          'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80',
          'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&auto=format&fit=crop&q=80',
          'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80',
          'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80',
          'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80',
        ];
        const mapped: TeamCandidate[] = recs.map((rec) => {
          const original = initialCandidates.find(
            (c) => c.id === `candidate-${rec.candidate_id}` || c.id === String(rec.candidate_id)
          );
          const avatar = original?.avatar || AVATARS[rec.candidate_id % AVATARS.length];
          return {
            id: `candidate-${rec.candidate_id}`,
            name: rec.candidate_name,
            role: rec.professional_role || rec.role_suggestion,
            level: rec.overall_proficiency || 'Intermediate',
            avatar,
            matchPercentage: Math.round(rec.match_score),
            aiInsight: rec.explanation,
            verifiedSkills: rec.verified_skills || [],
            skillsContributed: rec.skills_contributed || [],
            complementarySkills: rec.complementary_skills || [],
            missingSkills: rec.missing_team_skills || [],
            coreSkillsFulfilled: rec.core_skills_fulfilled || [],
            coreSkillsMissing: rec.core_skills_missing || [],
            invited: original?.invited || false,
            education: rec.university || original?.education || 'University Student',
            location: original?.location || 'India',
            matchedSkillsDetails: rec.matched_skills,
            professionalRole: rec.professional_role,
            verifiedDomains: rec.verified_domains,
            targetRole: rec.target_role,
            evidenceBreakdown: rec.evidence_breakdown,
          };
        });
        setCandidatesList(mapped);
      }
    } catch {
      // Keep existing list on error
    } finally {
      setIsFiltering(false);
    }
  };

  useEffect(() => {
    if (initialRoleFilter && initialRoleFilter !== 'All') {
      handleFilterChange(initialRoleFilter);
    }
  }, [initialRoleFilter]);

  // Derived joined members and pending invitations from live team record
  const joinedMembers = activeTeam ? activeTeam.members.filter(m => m.status === 'joined' && m.student_id !== activeTeam.creator_id) : [];
  const dbPendingInvitations = activeTeam?.invitations?.filter(i => i.status === 'PENDING') || [];
  
  const allPendingInvitations = [
    ...dbPendingInvitations.map(i => ({ name: i.recipient_name || `Candidate #${i.recipient_id}`, role: i.role })),
    ...candidatesList
      .filter(c => c.invited && !dbPendingInvitations.some(pi => pi.recipient_name === c.name || String(pi.recipient_id) === c.id))
      .map(c => ({ name: c.name, role: c.professionalRole || c.role })),
  ];

  const currentMembersCount = activeTeam 
    ? Math.max(1, activeTeam.members.filter(m => m.status === 'joined').length) 
    : 1;

  const teamCoverageScore = typeof activeTeam?.team_coverage_percentage === 'number'
    ? activeTeam.team_coverage_percentage
    : 20;

  const coveredList = activeTeam?.skills_covered && activeTeam.skills_covered.length > 0
    ? activeTeam.skills_covered
    : ['Frontend'];

  const missingList = activeTeam?.skills_missing && activeTeam.skills_missing.length > 0
    ? activeTeam.skills_missing
    : ['Backend', 'Database', 'AI/ML', 'UI/UX'];

  if (isLoading) {
    return (
      <main className="max-w-[1240px] mx-auto px-4 md:px-6 py-10 flex flex-col items-center justify-center min-h-[50vh] gap-3 font-['Inter']">
        <CircularProgress percentage={75} size={48} strokeWidth={4} color="#00687a" />
        <p className="text-xs font-semibold text-slate-600">
          Evaluating team requirement gaps and 5 core skills per domain...
        </p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="max-w-[1240px] mx-auto px-4 md:px-6 py-10 flex flex-col items-center justify-center min-h-[50vh] gap-3 font-['Inter']">
        <div className="w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center border border-red-200">
          <span className="material-symbols-outlined text-2xl">error</span>
        </div>
        <h2 className="text-lg font-bold text-slate-900">Failed to Load Team Candidates</h2>
        <p className="text-xs text-slate-600 text-center max-w-md">{error}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 px-5 py-2 bg-[#00687a] text-white text-xs font-bold rounded-full hover:bg-[#004e5c] transition-colors shadow-xs flex items-center gap-1.5"
          >
            <span className="material-symbols-outlined text-[15px]">refresh</span>
            <span>Retry Connection</span>
          </button>
        )}
      </main>
    );
  }

  return (
    <main className="max-w-[1240px] mx-auto px-4 sm:px-6 py-6 font-['Inter']">
      {/* Compact Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-['Hanken_Grotesk'] text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Multidisciplinary Team Builder
            </h1>
            <span className="bg-cyan-50 text-[#00687a] border border-cyan-200 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
              Deterministic 5-Core Gap Matching
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Discover peer candidates evaluated strictly against your team's unfilled capability requirements.
          </p>
        </div>

        <button
          onClick={() => onNavigate('my-team')}
          className="px-3.5 py-1.5 bg-[#00687a] hover:bg-[#00505e] text-white text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer shadow-xs"
        >
          <span className="material-symbols-outlined text-[16px]">diversity_3</span>
          <span>View My Team Roster</span>
        </button>
      </div>

      {/* Role Gap Filter Pills */}
      <div className="mt-4 flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider shrink-0 mr-1">
          Target Role:
        </span>
        {ROLE_FILTERS.map((rf) => {
          const isActive = activeRoleFilter === rf.value;
          return (
            <button
              key={rf.value}
              onClick={() => handleFilterChange(rf.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shrink-0 cursor-pointer ${
                isActive
                  ? 'bg-[#00687a] text-white shadow-xs'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              <span className="material-symbols-outlined text-[15px]">{rf.icon}</span>
              <span>{rf.name}</span>
            </button>
          );
        })}
      </div>

      {/* Main Grid: Candidate Cards + Stationary Sidebar */}
      <div className="mt-4 grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Candidate Feed */}
        <section className="lg:col-span-8 space-y-3.5">
          <div className="flex justify-between items-center text-xs text-slate-500 px-0.5">
            <span>
              Showing <strong className="text-slate-800">{candidatesList.length}</strong> evaluated candidates
              {activeRoleFilter !== 'All' && <span> for <strong>{activeRoleFilter}</strong></span>}
            </span>
            {isFiltering && (
              <span className="text-xs text-[#00687a] font-semibold flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px] animate-spin">progress_activity</span>
                Recalculating...
              </span>
            )}
          </div>

          {candidatesList.length === 0 ? (
            <div className="bg-white rounded-xl border border-dashed border-slate-300 p-8 text-center">
              <span className="material-symbols-outlined text-slate-400 text-4xl mb-1">person_search</span>
              <h3 className="text-sm font-bold text-slate-800">No matching candidates found</h3>
              <p className="text-xs text-slate-500 mt-1">No candidate students currently match this role filter.</p>
              <button
                onClick={() => handleFilterChange('All')}
                className="mt-3 px-3.5 py-1.5 bg-[#00687a] text-white text-xs font-bold rounded-lg cursor-pointer"
              >
                Show All Candidates
              </button>
            </div>
          ) : (
            candidatesList.map((candidate) => {
              // 5 Core domain requirements display
              const coreFulfilled = candidate.coreSkillsFulfilled && candidate.coreSkillsFulfilled.length > 0
                ? candidate.coreSkillsFulfilled
                : (candidate.skillsContributed || []).map((s) => `✓ ${s}`);
              
              const coreMissing = candidate.coreSkillsMissing && candidate.coreSkillsMissing.length > 0
                ? candidate.coreSkillsMissing
                : (candidate.missingSkills || []).map((s) => `✕ ${s}`);

              return (
                <article
                  key={candidate.id}
                  className="bg-white border border-slate-200 rounded-xl p-4 sm:p-4.5 flex flex-col gap-3 hover:border-slate-300 hover:shadow-xs transition-all"
                >
                  {/* Card Top: Avatar, Name, Selected Role, Circular Match */}
                  <div className="flex justify-between items-start gap-3">
                    <div className="flex items-center gap-3 min-w-0">
                      <img
                        src={candidate.avatar}
                        alt={candidate.name}
                        className="w-11 h-11 rounded-full object-cover border border-slate-200 shadow-2xs shrink-0"
                      />
                      <div className="min-w-0">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <h3 className="font-['Hanken_Grotesk'] text-base font-bold text-slate-900 truncate">
                            {candidate.name}
                          </h3>
                          <span className="material-symbols-outlined text-[#00687a] text-[16px] material-symbols-fill" title="Verified Skill Passport">
                            verified
                          </span>
                        </div>
                        
                        {/* Candidate's Selected Professional Role */}
                        <div className="flex items-center gap-1.5 mt-0.5 flex-wrap">
                          <span className="text-[11px] font-bold text-[#00687a] bg-cyan-50 px-1.5 py-0.2 rounded border border-cyan-200">
                            {candidate.professionalRole || candidate.role}
                          </span>
                          <span className="text-[11px] text-slate-400">
                            • {candidate.education}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Match Score */}
                    <div 
                      onClick={() => onOpenMatchModal(candidate)}
                      className="flex flex-col items-center cursor-pointer hover:scale-105 transition-transform shrink-0"
                      title="Click to view explainable requirement breakdown"
                    >
                      <CircularProgress
                        percentage={candidate.matchPercentage}
                        size={46}
                        strokeWidth={3.5}
                        color={candidate.matchPercentage >= 80 ? '#00687a' : candidate.matchPercentage >= 40 ? '#0284c7' : '#94a3b8'}
                        fontSize="text-[11px] font-bold"
                      />
                      <span className="text-[9px] font-bold text-[#00687a] mt-0.5">
                        {candidate.matchPercentage === 0 ? 'No Match' : `${candidate.matchPercentage}% Req`}
                      </span>
                    </div>
                  </div>

                  {/* 5 Core Domain Skills Badges (Fulfilled ✓ vs Missing ✕) */}
                  <div className="bg-slate-50/90 rounded-lg p-2.5 border border-slate-200/80">
                    <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                      <span>5 Core Domain Capabilities:</span>
                      <span className="text-slate-400 lowercase font-normal">{candidate.targetRole || 'Evaluation'}</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {coreFulfilled.map((skill, idx) => (
                        <span
                          key={`f-${idx}`}
                          className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded text-[11px] font-semibold flex items-center gap-1"
                        >
                          <span className="material-symbols-outlined text-[13px] text-emerald-600">check_circle</span>
                          {skill.replace(/^✓\s*/, '')}
                        </span>
                      ))}
                      {coreMissing.map((skill, idx) => (
                        <span
                          key={`m-${idx}`}
                          className="bg-rose-50/80 text-rose-800 border border-rose-200/80 px-2 py-0.5 rounded text-[11px] font-medium flex items-center gap-1"
                        >
                          <span className="material-symbols-outlined text-[13px] text-rose-500">cancel</span>
                          {skill.replace(/^✕\s*/, '')}
                        </span>
                      ))}
                      {coreFulfilled.length === 0 && coreMissing.length === 0 && (
                        <span className="text-[11px] text-slate-400 italic">No specific domain requirements mapped.</span>
                      )}
                    </div>
                  </div>

                  {/* Why Recommended / Explainable Match Note */}
                  <div className="bg-[#f2ecfd] text-[#280c5e] rounded-lg p-2.5 border border-[#d6c4f8] flex gap-2 items-start text-xs">
                    <span className="material-symbols-outlined text-[#6d3bd7] text-[16px] material-symbols-fill shrink-0 mt-0.5">
                      auto_awesome
                    </span>
                    <div className="flex-1 min-w-0">
                      <span className="text-[9px] font-bold uppercase tracking-wider block text-[#6d3bd7]">
                        WHY RECOMMENDED
                      </span>
                      <p className="text-[11px] text-slate-800 leading-snug">
                        {candidate.aiInsight}
                      </p>
                    </div>
                  </div>

                  {/* Actions: View Breakdown & Send Invitation */}
                  <div className="flex items-center justify-between pt-2 border-t border-slate-100 gap-2">
                    <button
                      onClick={() => onOpenMatchModal(candidate)}
                      className="px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold transition-colors flex items-center gap-1 cursor-pointer"
                    >
                      <span className="material-symbols-outlined text-[15px] text-[#00687a]">analytics</span>
                      <span>Match Breakdown</span>
                    </button>

                    <button
                      onClick={() => {
                        if (!candidate.invited) onInviteCandidate(candidate.id);
                      }}
                      disabled={candidate.invited}
                      className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 cursor-pointer ${
                        candidate.invited
                          ? 'bg-emerald-600 text-white cursor-default'
                          : 'bg-[#00687a] hover:bg-[#00505e] text-white shadow-xs'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[15px]">
                        {candidate.invited ? 'check' : 'person_add'}
                      </span>
                      <span>{candidate.invited ? 'Invitation Sent ✓' : 'Send Invitation'}</span>
                    </button>
                  </div>
                </article>
              );
            })
          )}
        </section>

        {/* Stationary Sidebar: Team Composition & Capabilities (NEVER overlaps or covers cards) */}
        <aside className="lg:col-span-4 relative static space-y-4">
          <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-2xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  Team Composition
                </span>
                <h3 className="font-['Hanken_Grotesk'] text-sm font-bold text-slate-900 truncate">
                  {activeTeam?.name || 'Hex Bridge'}
                </h3>
              </div>
              <span className="text-[11px] font-bold text-[#00687a] bg-cyan-50 px-2 py-0.5 rounded-full border border-cyan-200 shrink-0">
                {currentMembersCount}/6 Members
              </span>
            </div>

            {/* TEAM MEMBERS */}
            <div className="mt-3 space-y-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                Team Members
              </span>
              
              {/* Leader */}
              <div className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-50 border border-slate-200/80">
                <div className="w-8 h-8 rounded-full bg-[#00687a] text-white flex items-center justify-center font-bold text-xs shrink-0">
                  {(activeTeam?.creator_name || studentName).charAt(0)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold text-slate-900 truncate">
                      {activeTeam?.creator_name || studentName}
                    </p>
                    <span className="text-[9.5px] font-bold text-[#00687a] uppercase tracking-wider">
                      Team Leader
                    </span>
                  </div>
                  <span className="text-[10.5px] text-slate-500 block">
                    {activeTeam?.members.find(m => m.student_id === activeTeam?.creator_id)?.role || 'Project Lead'}
                  </span>
                </div>
              </div>

              {/* Joined Members */}
              {joinedMembers.map((member) => (
                <div key={member.id} className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-50/70 border border-slate-200/70">
                  <div className="w-8 h-8 rounded-full bg-cyan-100 text-[#00687a] flex items-center justify-center font-bold text-xs shrink-0">
                    {(member.student_name || 'M').charAt(0)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-xs font-bold text-slate-900 truncate">{member.student_name}</p>
                      <span className="text-[9.5px] font-semibold text-slate-500 uppercase tracking-wider">
                        Member
                      </span>
                    </div>
                    <span className="text-[10.5px] text-slate-500 block">
                      {member.professional_role || member.role}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* PENDING INVITATIONS */}
            {allPendingInvitations.length > 0 && (
              <div className="mt-3 pt-2.5 border-t border-slate-100 space-y-1.5">
                <span className="text-[10px] font-bold text-amber-700 uppercase tracking-wider block">
                  Pending Invitations ({allPendingInvitations.length})
                </span>
                {allPendingInvitations.map((inv, idx) => (
                  <div key={idx} className="flex items-center gap-2 p-1.5 rounded-lg bg-amber-50/60 border border-amber-200/70">
                    <span className="material-symbols-outlined text-[15px] text-amber-600 shrink-0">mail</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-[11px] font-bold text-slate-800 truncate">{inv.name}</p>
                      <span className="text-[9.5px] text-amber-700 block">
                        {inv.role} • Invitation Pending
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Team Capability Coverage Bar (Section 23 & 30) */}
            <div className="mt-4 pt-3 border-t border-slate-100">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-bold text-slate-700">Team Skill Coverage</span>
                <span className="text-xs font-bold text-[#00687a]">{teamCoverageScore}%</span>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-[#00687a] rounded-full transition-all duration-500"
                  style={{ width: `${teamCoverageScore}%` }}
                ></div>
              </div>
            </div>

            {/* Covered & Missing Capabilities */}
            <div className="mt-3 space-y-2 text-[11px]">
              <div>
                <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider block mb-1">
                  Covered Capabilities:
                </span>
                <div className="flex flex-wrap gap-1">
                  {coveredList.map((c) => (
                    <span key={c} className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-1.5 py-0.2 rounded text-[10px] font-semibold">
                      ✓ {c}
                    </span>
                  ))}
                  {coveredList.length === 0 && (
                    <span className="text-[10px] text-slate-400 italic">None yet</span>
                  )}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold text-amber-700 uppercase tracking-wider block mb-1">
                  Missing Capabilities:
                </span>
                <div className="flex flex-wrap gap-1">
                  {missingList.map((m) => (
                    <span key={m} className="bg-amber-50 text-amber-800 border border-amber-200 px-1.5 py-0.2 rounded text-[10px] font-semibold">
                      ✕ {m}
                    </span>
                  ))}
                  {missingList.length === 0 && (
                    <span className="text-[10px] text-emerald-700 font-semibold">All capabilities fulfilled!</span>
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={() => onNavigate('my-team')}
              className="w-full mt-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-xs rounded-lg border border-slate-300/80 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[15px]">diversity_3</span>
              <span>Manage Team & Requirements</span>
            </button>
          </div>
        </aside>
      </div>
    </main>
  );
};
