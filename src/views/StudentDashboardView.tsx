import React, { useState, useEffect } from 'react';
import { Internship, ActivityItem, ScreenType, ApiProfessionalProfile, ApiTeam } from '../types';
import { CircularProgress } from '../components/common/CircularProgress';
import { studentsApi } from '../api/students';
import { teamsApi } from '../api/teams';

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

const AVAILABLE_ROLES = [
  'Full Stack Developer',
  'Frontend Developer',
  'Backend Developer',
  'AI/ML Developer',
  'Data Scientist',
  'Data/Database Specialist',
  'DevOps & Cloud Engineer',
  'UI/UX Designer',
  'Cybersecurity Developer',
  'Mobile Developer',
];

const AVAILABLE_SPECIALIZATIONS = [
  'Frontend & UI',
  'Backend Development',
  'AI & Machine Learning',
  'Data Systems & Databases',
  'DevOps & Cloud',
  'UI/UX Design',
  'Cybersecurity',
  'Algorithms & DSA',
];

export const StudentDashboardView: React.FC<StudentDashboardProps> = ({
  studentName = 'Aarav Sharma',
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

  // Professional Identity State
  const [profile, setProfile] = useState<ApiProfessionalProfile | null>(null);
  const [myTeam, setMyTeam] = useState<ApiTeam | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState('Full Stack Developer');
  const [selectedSpecs, setSelectedSpecs] = useState<string[]>([]);
  const [bioInput, setBioInput] = useState('');
  const [isSavingRole, setIsSavingRole] = useState(false);
  const [modalWarning, setModalWarning] = useState<string | null>(null);

  // Dynamic formula: 0 skills = 0%, 1 = 20%, 2 = 40%, 3 = 60%, 4 = 80%, 5+ = 100%
  const dynamicCompletion = typeof completionPercentage === 'number' 
    ? completionPercentage 
    : Math.min(100, verifiedSkillsCount * 20);

  useEffect(() => {
    let isMounted = true;
    
    // Fetch Professional Role
    studentsApi.getMyProfessionalRole()
      .then((data) => {
        if (isMounted && data) {
          setProfile(data);
          setSelectedRole(data.primary_role);
          setSelectedSpecs(data.secondary_specializations || []);
          setBioInput(data.bio || '');
        }
      })
      .catch(() => {
        // Safe fallback
      });

    // Fetch My Team
    teamsApi.getMyTeams()
      .then((teams) => {
        if (isMounted && teams && teams.length > 0) {
          setMyTeam(teams[0]);
        }
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, []);

  const handleOpenEditModal = () => {
    if (profile) {
      setSelectedRole(profile.primary_role);
      setSelectedSpecs(profile.secondary_specializations || []);
      setBioInput(profile.bio || '');
      setModalWarning(null);
    }
    setIsEditModalOpen(true);
  };

  const handleRoleSelection = (role: string) => {
    setSelectedRole(role);
    if (profile) {
      const roleAnalysis = profile.supported_roles?.find((r) => r.role === role);
      if (roleAnalysis && !roleAnalysis.is_supported) {
        setModalWarning(
          `Notice: '${role}' requires verified competencies in ${roleAnalysis.missing_domains.join(', ')}. Your Skill Passport currently has insufficient verified evidence for these areas.`
        );
      } else {
        setModalWarning(null);
      }
    }
  };

  const toggleSpecialization = (spec: string) => {
    if (selectedSpecs.includes(spec)) {
      setSelectedSpecs(selectedSpecs.filter((s) => s !== spec));
    } else {
      setSelectedSpecs([...selectedSpecs, spec]);
    }
  };

  const handleSaveRole = async () => {
    setIsSavingRole(true);
    try {
      const updated = await studentsApi.updateMyProfessionalRole({
        primary_role: selectedRole,
        secondary_specializations: selectedSpecs,
        bio: bioInput,
      });
      setProfile(updated);
      setIsEditModalOpen(false);
    } catch (err: any) {
      setModalWarning(err?.message || 'Failed to save professional identity.');
    } finally {
      setIsSavingRole(false);
    }
  };

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
    <main className="max-w-[1240px] mx-auto p-4 sm:px-6 sm:py-6 flex flex-col gap-4 sm:gap-5 pb-20 md:pb-10 min-h-screen font-['Inter']">
      {/* Greeting Header */}
      <section className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl font-bold text-[#191c1e] tracking-tight">
            Hi, {firstName}!
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
            Verified skill passport progress, multidisciplinary teams, and explainable opportunities.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('my-team')}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-lg border border-slate-300/80 transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[16px] text-[#00687a]">diversity_3</span>
            <span>My Team</span>
          </button>
          <button
            onClick={() => onNavigate('add-evidence')}
            className="px-3.5 py-1.5 bg-[#00687a] hover:bg-[#00505e] text-white font-semibold text-xs rounded-lg shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[16px]">add_circle</span>
            <span>Add Evidence</span>
          </button>
        </div>
      </section>

      {/* SECTION: YOUR PROFESSIONAL IDENTITY */}
      <section className="bg-gradient-to-br from-white to-cyan-50/40 border border-slate-200 rounded-xl p-4 sm:p-5 shadow-2xs relative overflow-hidden">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-cyan-100 text-[#00687a] flex items-center justify-center font-bold shrink-0">
              <span className="material-symbols-outlined text-[22px]">badge</span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#00687a] bg-cyan-100/60 px-2 py-0.2 rounded-full">
                  Team Builder Identity
                </span>
                <span className="text-[11px] text-slate-400 font-medium">• Evidence-Backed</span>
              </div>
              <h2 className="font-['Hanken_Grotesk'] text-xl font-bold text-slate-900 mt-0.5">
                {profile?.primary_role || 'Full Stack Developer'}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <span className="text-[11px] font-bold text-slate-400 block uppercase tracking-wider">Overall Proficiency</span>
              <span className={`text-sm font-bold ${
                profile?.overall_proficiency === 'Advanced' ? 'text-emerald-700' :
                profile?.overall_proficiency === 'Intermediate' ? 'text-cyan-800' : 'text-slate-700'
              }`}>
                {profile?.overall_proficiency || (verifiedSkillsCount >= 2 ? 'Intermediate' : 'Proficiency not yet established')}
              </span>
            </div>
            <button
              onClick={handleOpenEditModal}
              className="px-4 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-slate-800 font-semibold text-xs transition-colors shadow-2xs flex items-center gap-1.5 shrink-0"
            >
              <span className="material-symbols-outlined text-[16px] text-[#00687a]">tune</span>
              <span>Customize Role</span>
            </button>
          </div>
        </div>

        {/* Verified Domain Proficiencies Cards */}
        <div className="mt-5">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
            Verified Domain Proficiencies & Evidence
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {profile?.domain_proficiencies?.filter((d) => d.is_supported).map((d) => (
              <div key={d.domain} className="bg-white border border-slate-200/90 rounded-xl p-3.5 shadow-2xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800">{d.domain}</span>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {d.proficiency}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1.5 flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px] text-emerald-600">verified</span>
                  <span>{d.verified_skills_count} verified skills ({d.verified_skills.slice(0, 2).join(', ')})</span>
                </p>
              </div>
            ))}

            {(!profile?.domain_proficiencies || profile.domain_proficiencies.filter((d) => d.is_supported).length === 0) && (
              <div className="col-span-full bg-amber-50/70 border border-amber-200 rounded-xl p-4 text-xs text-amber-800 flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">info</span>
                <span>No verified domain evidence yet. Add coursework or repository projects to establish verified domain proficiency.</span>
              </div>
            )}
          </div>
        </div>

        {/* Secondary Specializations */}
        {profile?.secondary_specializations && profile.secondary_specializations.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold text-slate-500">Secondary Specializations:</span>
            {profile.secondary_specializations.map((spec) => (
              <span key={spec} className="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200">
                {spec}
              </span>
            ))}
          </div>
        )}
      </section>

      {/* SECTION: MY PROJECT TEAM STATUS */}
      <section className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center font-bold border border-purple-100 shrink-0">
              <span className="material-symbols-outlined text-[22px]">diversity_3</span>
            </div>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-purple-700 bg-purple-50 px-2 py-0.2 rounded-full">
                {myTeam ? 'Active Project Team' : 'Team Collaboration'}
              </span>
              <h3 className="font-['Hanken_Grotesk'] text-lg font-bold text-slate-900 mt-0.5">
                {myTeam ? myTeam.name : 'You are not part of a project team yet'}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {myTeam ? (myTeam.project_name || myTeam.description) : 'Form an interdisciplinary team or join existing projects to collaborate.'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {myTeam ? (
              <button
                onClick={() => onNavigate('my-team')}
                className="px-4 py-2 bg-[#00687a] hover:bg-[#00505e] text-white font-semibold text-xs rounded-lg shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
              >
                <span>Open My Team</span>
                <span className="material-symbols-outlined text-[15px]">arrow_forward</span>
              </button>
            ) : (
              <>
                <button
                  onClick={() => onNavigate('my-team')}
                  className="px-3.5 py-1.5 bg-[#00687a] hover:bg-[#00505e] text-white font-semibold text-xs rounded-lg shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[15px]">add</span>
                  <span>Create Team</span>
                </button>
                <button
                  onClick={() => onNavigate('team-builder')}
                  className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-lg border border-slate-300 transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[15px]">search</span>
                  <span>Find Teammates</span>
                </button>
              </>
            )}
          </div>
        </div>

        {myTeam && (
          <div className="mt-5 pt-4 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/80">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Team Capacity</span>
              <p className="text-base font-bold text-slate-800 mt-0.5">
                {myTeam.total_members_count ?? myTeam.members.filter((m) => m.status === 'joined').length} / 6 Members
              </p>
            </div>

            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/80">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Skill Gap Coverage</span>
              <div className="flex items-center gap-2 mt-1">
                <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-[#10b981] rounded-full"
                    style={{ width: `${myTeam.team_coverage_percentage ?? 60}%` }}
                  ></div>
                </div>
                <span className="text-xs font-bold text-slate-800">{myTeam.team_coverage_percentage ?? 60}%</span>
              </div>
            </div>

            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/80">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Missing Capabilities</span>
              <p className="text-xs font-semibold text-amber-700 mt-1 truncate">
                {myTeam.skills_missing && myTeam.skills_missing.length > 0 
                  ? myTeam.skills_missing.slice(0, 3).join(', ')
                  : 'All core skills fulfilled!'}
              </p>
            </div>
          </div>
        )}
      </section>

      {/* Bento Grid: Passport Completion & Key Stats */}
      <section className="grid grid-cols-1 md:grid-cols-12 gap-3.5 sm:gap-4">
        {/* Passport Completion Card */}
        <div 
          onClick={() => onNavigate('passport')}
          className="md:col-span-8 bg-white border border-slate-200 rounded-xl p-4 sm:p-5 flex flex-col justify-between shadow-2xs hover:shadow-xs transition-shadow relative overflow-hidden group cursor-pointer"
        >
          <div className="absolute -right-16 -top-16 w-64 h-64 bg-cyan-100/40 rounded-full blur-3xl group-hover:opacity-100 opacity-50 transition-opacity pointer-events-none"></div>

          <div className="flex justify-between items-start mb-4 relative z-10">
            <div>
              <h2 className="font-['Hanken_Grotesk'] text-lg sm:text-xl font-bold text-[#191c1e]">
                Passport Completion
              </h2>
              <p className="text-xs text-slate-600 mt-0.5">
                Your core competencies are dynamically calculated from verified artifacts.
              </p>
            </div>
            <div className="w-8 h-8 rounded-full bg-[#f2f4f6] flex items-center justify-center text-[#00687a] border border-slate-200 shadow-2xs">
              <span className="material-symbols-outlined material-symbols-fill text-[18px]">verified</span>
            </div>
          </div>

          <div className="relative z-10">
            <div className="flex justify-between items-end mb-1.5">
              <span className="font-['Hanken_Grotesk'] text-3xl sm:text-4xl font-bold text-[#191c1e]">
                {dynamicCompletion}%
              </span>
              <span className="text-xs font-bold text-[#00687a]">
                {dynamicCompletion > 0 ? `${verifiedSkillsCount} Verified Skill${verifiedSkillsCount > 1 ? 's' : ''}` : 'Start Building Passport'}
              </span>
            </div>
            <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-[#00687a] rounded-full relative overflow-hidden transition-all duration-1000"
                style={{ width: `${dynamicCompletion}%` }}
              >
                <div className="absolute inset-0 bg-white/25 w-full h-full transform -skew-x-12 animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Key Stats Grid */}
        <div className="md:col-span-4 grid grid-cols-2 md:grid-cols-1 gap-3 md:gap-4">
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

      {/* MODAL: Customize Professional Identity */}
      {isEditModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center pb-3 border-b border-slate-100">
              <div>
                <h3 className="font-['Hanken_Grotesk'] text-xl font-bold text-slate-900">
                  Customize Professional Role
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Choose how your verified profile is represented in Team Builder matching.
                </p>
              </div>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="w-8 h-8 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 flex items-center justify-center"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            {/* Role selection alert if unsupported */}
            {modalWarning && (
              <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 flex items-start gap-2">
                <span className="material-symbols-outlined text-[18px] text-amber-600 shrink-0 mt-0.5">warning</span>
                <span>{modalWarning}</span>
              </div>
            )}

            <div className="mt-5 space-y-4">
              {/* Primary Role Selector */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                  Primary Role for Team Builder
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {AVAILABLE_ROLES.map((role) => {
                    const roleSupport = profile?.supported_roles?.find((r) => r.role === role);
                    const isSupported = roleSupport ? roleSupport.is_supported : true;
                    const isSelected = selectedRole === role;

                    return (
                      <button
                        key={role}
                        type="button"
                        onClick={() => handleRoleSelection(role)}
                        className={`p-3 rounded-xl border text-left flex items-center justify-between transition-all ${
                          isSelected
                            ? 'bg-cyan-50 border-[#00687a] ring-1 ring-[#00687a]'
                            : 'bg-white border-slate-200 hover:bg-slate-50'
                        }`}
                      >
                        <div>
                          <p className={`text-xs font-bold ${isSelected ? 'text-[#00687a]' : 'text-slate-800'}`}>
                            {role}
                          </p>
                          <span className="text-[10px] text-slate-400">
                            {isSupported ? '✓ Supported by passport' : '⚠ Limited verified evidence'}
                          </span>
                        </div>
                        {isSelected && (
                          <span className="material-symbols-outlined text-[18px] text-[#00687a]">check_circle</span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Secondary Specializations Multiselect */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                  Secondary Specializations (Select all that apply)
                </label>
                <div className="flex flex-wrap gap-2">
                  {AVAILABLE_SPECIALIZATIONS.map((spec) => {
                    const isSelected = selectedSpecs.includes(spec);
                    return (
                      <button
                        key={spec}
                        type="button"
                        onClick={() => toggleSpecialization(spec)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                          isSelected
                            ? 'bg-[#00687a] text-white border-[#00687a]'
                            : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
                        }`}
                      >
                        {spec} {isSelected ? '✓' : '+'}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Bio / Objective */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Professional Statement & Objective
                </label>
                <textarea
                  value={bioInput}
                  onChange={(e) => setBioInput(e.target.value)}
                  rows={3}
                  placeholder="Describe your technical focus, project interests, and team contributions..."
                  className="w-full text-xs p-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#00687a] resize-none"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setIsEditModalOpen(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveRole}
                disabled={isSavingRole}
                className="px-6 py-2 bg-[#00687a] hover:bg-[#00505e] text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                {isSavingRole ? (
                  <>
                    <span className="material-symbols-outlined text-[16px] animate-spin">progress_activity</span>
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-[16px]">save</span>
                    <span>Save Professional Identity</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
};
