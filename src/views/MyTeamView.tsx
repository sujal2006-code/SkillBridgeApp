import React, { useState, useEffect } from 'react';
import { ApiTeam, ScreenType, ApiTeamMember } from '../types';
import { teamsApi, CreateTeamPayload } from '../api/teams';
import { CircularProgress } from '../components/common/CircularProgress';
import { getStudentAvatar } from '../utils/avatars';

interface MyTeamViewProps {
  studentName?: string;
  studentId?: number;
  onNavigate: (screen: ScreenType) => void;
  onSelectMissingDomain?: (domain: string) => void;
}

const COMMON_DOMAINS = [
  'Frontend & UI',
  'Backend Development',
  'AI & Machine Learning',
  'Data Systems & Databases',
  'DevOps & Cloud',
  'UI/UX Design',
];

export const MyTeamView: React.FC<MyTeamViewProps> = ({
  studentName = 'Student',
  studentId = 1,
  onNavigate,
  onSelectMissingDomain,
}) => {
  const [teams, setTeams] = useState<ApiTeam[]>([]);
  const [activeTeam, setActiveTeam] = useState<ApiTeam | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Creation Modal State
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newTeamName, setNewTeamName] = useState('');
  const [newProjectName, setNewProjectName] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [selectedDomains, setSelectedDomains] = useState<string[]>(['Frontend & UI', 'Backend Development']);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const fetchMyTeams = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await teamsApi.getMyTeams();
      setTeams(data || []);
      if (data && data.length > 0) {
        setActiveTeam(data[0]);
      } else {
        setActiveTeam(null);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load your project teams.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMyTeams();
  }, []);

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTeamName.trim()) {
      setCreateError('Team name is required.');
      return;
    }

    setIsSubmitting(true);
    setCreateError(null);

    try {
      const payload: CreateTeamPayload = {
        name: newTeamName.trim(),
        project_name: newProjectName.trim() || newTeamName.trim(),
        description: newDescription.trim() || undefined,
        creator_id: studentId,
        required_domains: selectedDomains,
      };

      const created = await teamsApi.createTeam(payload);
      setTeams([created, ...teams]);
      setActiveTeam(created);
      setIsCreateModalOpen(false);
      setNewTeamName('');
      setNewProjectName('');
      setNewDescription('');
    } catch (err: any) {
      setCreateError(err?.message || 'Failed to create team.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleDomain = (domain: string) => {
    if (selectedDomains.includes(domain)) {
      setSelectedDomains(selectedDomains.filter((d) => d !== domain));
    } else {
      setSelectedDomains([...selectedDomains, domain]);
    }
  };

  const isLeader = activeTeam ? activeTeam.creator_id === studentId : false;
  const acceptedMembers = activeTeam ? activeTeam.members.filter((m) => m.status === 'joined') : [];
  const pendingInvitations = activeTeam?.invitations?.filter((i) => i.status === 'PENDING') || [];

  if (isLoading) {
    return (
      <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-16 flex flex-col items-center justify-center min-h-[60vh] gap-4 font-['Inter']">
        <CircularProgress percentage={75} size={56} strokeWidth={4.5} color="#00687a" />
        <p className="text-sm font-semibold text-slate-600">Loading your project teams and skill coverage...</p>
      </main>
    );
  }

  return (
    <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-8 min-h-screen font-['Inter']">
      {/* Top Header */}
      <section className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-[#00687a] uppercase tracking-wider bg-cyan-50 px-2.5 py-0.5 rounded-full border border-cyan-200">
              Multidisciplinary Team Hub
            </span>
            <span className="text-xs text-slate-400 font-medium">• Persistent Database Synced</span>
          </div>
          <h1 className="font-['Hanken_Grotesk'] text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight">
            My Project Team
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Monitor member capabilities, track combined skill coverage, and fill unfilled requirement gaps.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-4 py-2.5 bg-[#00687a] hover:bg-[#00505e] text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            <span>Create New Team</span>
          </button>
          <button
            onClick={() => onNavigate('team-builder')}
            className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl border border-slate-300 transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px] text-[#00687a]">search</span>
            <span>Find Teammates</span>
          </button>
        </div>
      </section>

      {/* Multiple Teams Switcher (if user has more than 1) */}
      {teams.length > 1 && (
        <section className="mb-6 flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          <span className="text-xs font-bold text-slate-500 mr-2">Your Teams:</span>
          {teams.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTeam(t)}
              className={`px-4 py-2 rounded-xl text-xs font-bold border transition-all ${
                activeTeam?.id === t.id
                  ? 'bg-[#00687a] text-white border-[#00687a] shadow-xs'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
            >
              {t.name}
            </button>
          ))}
        </section>
      )}

      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-['Hanken_Grotesk'] text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              My Project Team
            </h1>
            <span className="bg-cyan-50 text-[#00687a] border border-cyan-200 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
              Multidisciplinary
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage your project team, inspect collective capability coverage, and address skill gaps.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('team-builder')}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-lg border border-slate-300/80 transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[15px] text-[#00687a]">search</span>
            <span>Find Teammates</span>
          </button>

          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-3.5 py-1.5 bg-[#00687a] hover:bg-[#00505e] text-white font-semibold text-xs rounded-lg shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[15px]">add</span>
            <span>Create New Team</span>
          </button>
        </div>
      </div>

      {/* EMPTY STATE */}
      {!activeTeam && (
        <section className="mt-6 bg-white border border-slate-200 rounded-xl p-8 text-center max-w-xl mx-auto shadow-2xs">
          <div className="w-14 h-14 rounded-full bg-cyan-50 text-[#00687a] flex items-center justify-center mx-auto mb-3 border border-cyan-100">
            <span className="material-symbols-outlined text-3xl">diversity_3</span>
          </div>
          <h2 className="font-['Hanken_Grotesk'] text-lg font-bold text-slate-900">
            You are not part of a project team yet
          </h2>
          <p className="text-xs text-slate-600 mt-1 max-w-md mx-auto leading-relaxed">
            Form an interdisciplinary team with peers across AI/ML, Backend, Frontend, and Data systems, 
            or search for teams seeking your verified capabilities.
          </p>
          <div className="mt-5 flex flex-col sm:flex-row items-center justify-center gap-2.5">
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="w-full sm:w-auto px-4.5 py-2 bg-[#00687a] hover:bg-[#00505e] text-white font-semibold text-xs rounded-lg shadow-xs transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">add_circle</span>
              <span>Create a Team</span>
            </button>
            <button
              onClick={() => onNavigate('team-builder')}
              className="w-full sm:w-auto px-4.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-lg border border-slate-300 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px] text-[#00687a]">groups</span>
              <span>Explore Candidates</span>
            </button>
          </div>
        </section>
      )}

      {/* ACTIVE TEAM STATE */}
      {activeTeam && (
        <div className="mt-5 space-y-4">
          {/* Active Team Header Card */}
          <section className="bg-gradient-to-r from-slate-900 to-[#003844] text-white rounded-xl p-5 sm:p-6 shadow-sm relative overflow-hidden">
            <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="px-2 py-0.2 rounded-full bg-cyan-400/20 text-cyan-200 text-[10px] font-bold uppercase tracking-wider border border-cyan-400/30">
                    {isLeader ? 'You are Team Leader' : 'Team Member'}
                  </span>
                  <span className="text-[11px] text-white/60">
                    Created {new Date(activeTeam.created_at).toLocaleDateString()}
                  </span>
                </div>

                <h2 className="font-['Hanken_Grotesk'] text-xl sm:text-2xl font-bold tracking-tight text-white">
                  {activeTeam.name}
                </h2>
                <p className="text-cyan-100/90 text-xs font-semibold mt-0.5">
                  Project: {activeTeam.project_name || activeTeam.name}
                </p>
                {activeTeam.description && (
                  <p className="text-white/70 text-xs mt-1.5 max-w-2xl leading-relaxed">
                    {activeTeam.description}
                  </p>
                )}
              </div>

              {/* Quick stats on the right */}
              <div className="flex items-center gap-3 shrink-0 bg-white/10 backdrop-blur-md rounded-xl p-3 border border-white/15">
                <div className="text-center px-1.5">
                  <span className="text-xl font-bold text-white block">
                    {acceptedMembers.length}
                    <span className="text-xs text-white/60 font-normal"> / 6</span>
                  </span>
                  <span className="text-[9px] uppercase font-bold tracking-wider text-cyan-200">
                    Members
                  </span>
                </div>
                <div className="h-6 w-px bg-white/20"></div>
                <div className="text-center px-1.5">
                  <span className="text-xl font-bold text-[#10b981] block">
                    {activeTeam.team_coverage_percentage ?? 0}%
                  </span>
                  <span className="text-[9px] uppercase font-bold tracking-wider text-cyan-200">
                    Coverage
                  </span>
                </div>
              </div>
            </div>
          </section>

          {/* COMBINED TEAM SKILL COVERAGE SECTION */}
          <section className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-2xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
              <div>
                <h3 className="font-['Hanken_Grotesk'] text-xl font-bold text-slate-900 flex items-center gap-2">
                  <span>Team Skill Coverage</span>
                  <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                    {activeTeam.team_coverage_percentage ?? 0}% Fulfilled
                  </span>
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Aggregate verified capabilities across all accepted team members.
                </p>
              </div>

              <div className="w-full sm:w-48">
                <div className="flex justify-between items-center text-xs font-bold mb-1 text-slate-600">
                  <span>Coverage</span>
                  <span>{activeTeam.team_coverage_percentage ?? 0}%</span>
                </div>
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#10b981] rounded-full transition-all duration-500"
                    style={{ width: `${activeTeam.team_coverage_percentage ?? 0}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Capability Gaps / Requirements Grid */}
            <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Covered Capabilities */}
              <div className="bg-emerald-50/40 border border-emerald-200/70 rounded-2xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[16px] text-emerald-600">check_circle</span>
                    Covered Capabilities ({activeTeam.skills_covered?.length || 0})
                  </span>
                </div>

                {activeTeam.skills_covered && activeTeam.skills_covered.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {activeTeam.skills_covered.map((skill) => (
                      <span
                        key={skill}
                        className="px-2.5 py-1 rounded-lg bg-white border border-emerald-300 text-xs font-semibold text-emerald-800 flex items-center gap-1 shadow-2xs"
                      >
                        <span>✓</span>
                        <span>{skill}</span>
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400">No capabilities verified yet across current members.</p>
                )}
              </div>

              {/* Missing Capabilities & Direct Gap Action */}
              <div className="bg-amber-50/40 border border-amber-200/70 rounded-2xl p-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-amber-800 flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[16px] text-amber-600">warning</span>
                      Missing Capabilities ({activeTeam.skills_missing?.length || 0})
                    </span>
                  </div>

                  {activeTeam.skills_missing && activeTeam.skills_missing.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {activeTeam.skills_missing.map((skill) => (
                        <span
                          key={skill}
                          className="px-2.5 py-1 rounded-lg bg-white border border-amber-300 text-xs font-semibold text-amber-900 flex items-center gap-1 shadow-2xs"
                        >
                          <span>✕</span>
                          <span>{skill}</span>
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-emerald-700 font-semibold mb-4">
                      All required team capabilities are completely satisfied!
                    </p>
                  )}
                </div>

                {activeTeam.skills_missing && activeTeam.skills_missing.length > 0 && (
                  <button
                    onClick={() => {
                      if (onSelectMissingDomain) {
                        onSelectMissingDomain(activeTeam.skills_missing![0]);
                      }
                      onNavigate('team-builder');
                    }}
                    className="w-full py-2 bg-[#00687a] hover:bg-[#00505e] text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center justify-center gap-1.5 mt-2"
                  >
                    <span className="material-symbols-outlined text-[16px]">person_search</span>
                    <span>Find Teammate for {activeTeam.skills_missing[0]}</span>
                  </button>
                )}
              </div>
            </div>
          </section>

          {/* MEMBER ROSTER */}
          <section className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-2xs">
            <div className="flex justify-between items-center pb-3 border-b border-slate-100">
              <div>
                <h3 className="font-['Hanken_Grotesk'] text-lg font-bold text-slate-900">
                  Team Member Roster ({acceptedMembers.length}/6)
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Verified domains, individual proficiencies, and evidence artifacts.
                </p>
              </div>

              <button
                onClick={() => onNavigate('team-builder')}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-lg border border-slate-200 transition-colors flex items-center gap-1.5 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[15px]">person_add</span>
                <span>Invite Members</span>
              </button>
            </div>

            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {acceptedMembers.map((member) => (
                <div
                  key={member.id}
                  className="bg-slate-50/70 border border-slate-200 rounded-xl p-4 hover:bg-white hover:shadow-xs transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between mb-2.5">
                      <div className="flex items-center gap-2.5">
                        <img
                          src={getStudentAvatar(member.student_name || '', member.student_id)}
                          alt={member.student_name || 'Member'}
                          className="w-10 h-10 rounded-lg object-cover shadow-2xs shrink-0 border border-slate-200"
                        />
                        <div>
                          <h4 className="font-['Hanken_Grotesk'] text-sm font-bold text-slate-900 flex items-center gap-1">
                            {member.student_name || `Student #${member.student_id}`}
                            <span className="material-symbols-outlined text-[#00687a] text-[15px] material-symbols-fill">
                              verified
                            </span>
                          </h4>
                          <div className="flex items-center gap-1.5 mt-0.5">
                            <span className="text-[11px] font-bold text-[#00687a] bg-cyan-50 px-1.5 py-0.2 rounded border border-cyan-200">
                              {member.professional_role || member.role}
                            </span>
                            <span className="text-[11px] font-semibold text-slate-500">
                              • {member.proficiency || 'Intermediate'}
                            </span>
                          </div>
                        </div>
                      </div>

                      <span className={`text-[9.5px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                        member.role === 'Team Leader'
                          ? 'bg-purple-100 text-purple-800'
                          : 'bg-slate-200 text-slate-700'
                      }`}>
                        {member.role}
                      </span>
                    </div>

                    {/* Verified Skills */}
                    {member.verified_skills && member.verified_skills.length > 0 && (
                      <div className="mt-3">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                          Verified Skills
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {member.verified_skills.map((skill) => (
                            <span
                              key={skill}
                              className="px-2 py-0.5 rounded bg-white text-slate-700 border border-slate-200 text-[11px] font-medium"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Evidence Artifacts */}
                    {member.evidence_items && member.evidence_items.length > 0 && (
                      <div className="mt-3 pt-2 border-t border-slate-200/60">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                          Supporting Evidence Artifacts
                        </span>
                        <div className="space-y-0.5">
                          {member.evidence_items.slice(0, 2).map((ev, i) => (
                            <p key={i} className="text-[11px] text-slate-600 flex items-center gap-1 truncate">
                              <span className="material-symbols-outlined text-[13px] text-emerald-600 shrink-0">verified</span>
                              <span className="truncate">{ev}</span>
                            </p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* INVITATION STATUS (LEADER VIEW) */}
          {pendingInvitations.length > 0 && (
            <section className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs">
              <h3 className="font-['Hanken_Grotesk'] text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
                <span className="material-symbols-outlined text-amber-600">hourglass_top</span>
                <span>Pending Sent Invitations ({pendingInvitations.length})</span>
              </h3>

              <div className="divide-y divide-slate-100">
                {pendingInvitations.map((inv) => (
                  <div key={inv.id} className="py-3 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-slate-800">
                        Sent to: {inv.recipient_name || `Student #${inv.recipient_id}`}
                      </p>
                      <span className="text-[11px] text-slate-500">
                        Role: {inv.role} • Sent {new Date(inv.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
                      Pending Response
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {/* MODAL: CREATE TEAM */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl border border-slate-200">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100">
              <div>
                <h3 className="font-['Hanken_Grotesk'] text-xl font-bold text-slate-900">
                  Create a Project Team
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  You will automatically become Team Leader.
                </p>
              </div>
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="w-8 h-8 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 flex items-center justify-center"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            {createError && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-800 flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">error</span>
                <span>{createError}</span>
              </div>
            )}

            <form onSubmit={handleCreateTeam} className="mt-5 space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Team Name *
                </label>
                <input
                  type="text"
                  required
                  value={newTeamName}
                  onChange={(e) => setNewTeamName(e.target.value)}
                  placeholder="e.g. AI Vision Core Team"
                  className="w-full text-xs p-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#00687a]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Project Title / Initiative
                </label>
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="e.g. Real-Time Autonomous Navigation"
                  className="w-full text-xs p-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#00687a]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Project Description
                </label>
                <textarea
                  rows={2}
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Briefly describe what this team will construct..."
                  className="w-full text-xs p-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#00687a] resize-none"
                />
              </div>

              {/* Required Domains Selector */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                  Required Team Capability Domains
                </label>
                <div className="flex flex-wrap gap-2">
                  {COMMON_DOMAINS.map((domain) => {
                    const isSelected = selectedDomains.includes(domain);
                    return (
                      <button
                        key={domain}
                        type="button"
                        onClick={() => toggleDomain(domain)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                          isSelected
                            ? 'bg-[#00687a] text-white border-[#00687a]'
                            : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
                        }`}
                      >
                        {domain} {isSelected ? '✓' : '+'}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-2.5 bg-[#00687a] hover:bg-[#00505e] text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                  {isSubmitting ? 'Creating...' : 'Form Project Team'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
};
