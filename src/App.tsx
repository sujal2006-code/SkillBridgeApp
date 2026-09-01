import React, { useState, useEffect, useCallback } from 'react';
import {
  ScreenType,
  EvidenceItem,
  Skill,
  Internship,
  TeamCandidate,
  VerificationRequest,
  ActivityItem,
  ApiStudent,
  ApiRecommendation,
  ApiTeamCandidateRecommendation,
  ApiActivity,
  ApiStudentLoginResponse,
  ApiTeam,
} from './types';
import {
  studentsApi,
  recommendationsApi,
  internshipsApi,
  evidenceApi,
  teamsApi,
  activitiesApi,
  adminApi,
} from './api';
import { Navbar } from './components/layout/Navbar';
import { BottomNav } from './components/layout/BottomNav';
import { EvidenceModal } from './components/common/EvidenceModal';
import { MatchModal } from './components/common/MatchModal';
import { Toast } from './components/common/Toast';

import { LoginView } from './views/LoginView';
import { LandingView } from './views/LandingView';
import { PassportView } from './views/PassportView';
import { StudentDashboardView } from './views/StudentDashboardView';
import { InternshipsView } from './views/InternshipsView';
import { TeamBuilderView } from './views/TeamBuilderView';
import { MyTeamView } from './views/MyTeamView';
import { AddEvidenceView } from './views/AddEvidenceView';
import { AdminDashboardView } from './views/AdminDashboardView';
import { AdminLoginView } from './views/AdminLoginView';

const LOGO_MAP: { [key: string]: string } = {
  'NeuroTech Innovations': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=100&auto=format&fit=crop&q=80',
  'CloudSphere Dynamics': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=100&auto=format&fit=crop&q=80',
  'Boston Dynamics Partner': 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=100&auto=format&fit=crop&q=80',
  'Apex Data Labs': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=100&auto=format&fit=crop&q=80',
};

const DEFAULT_LOGO = 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=100&auto=format&fit=crop&q=80';

const AVATAR_LIST = [
  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&auto=format&fit=crop&q=80',
];

const VALID_SCREENS: ScreenType[] = [
  'login', 'landing', 'passport', 'dashboard',
  'internships', 'team-builder', 'my-team', 'add-evidence', 'admin', 'admin-login'
];

export default function App() {
  const [authToken, setAuthToken] = useState<string | null>(() => {
    return localStorage.getItem('skillbridge_auth_token');
  });
  const [activeStudentId, setActiveStudentId] = useState<number | null>(() => {
    const saved = localStorage.getItem('skillbridge_student_id');
    return saved ? Number(saved) : null;
  });
  const [currentScreen, setCurrentScreen] = useState<ScreenType>(() => {
    const hash = window.location.hash.replace('#/', '').trim();
    if (hash && VALID_SCREENS.includes(hash as ScreenType)) {
      return hash as ScreenType;
    }
    const token = localStorage.getItem('skillbridge_auth_token');
    if (!token) return 'login';
    const savedScreen = localStorage.getItem('skillbridge_last_screen') as ScreenType;
    return savedScreen && savedScreen !== 'login' ? savedScreen : 'dashboard';
  });
  const [adminToken, setAdminToken] = useState<string | null>(() => {
    return localStorage.getItem('skillbridge_admin_token');
  });
  const [activeTeamId, setActiveTeamId] = useState<number | null>(null);
  const [activeTeam, setActiveTeam] = useState<ApiTeam | null>(null);
  const [teamRoleFilter, setTeamRoleFilter] = useState<string>('All');
  
  // App state backed by live FastAPI backend & Neon PostgreSQL
  const [student, setStudent] = useState<ApiStudent | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [internships, setInternships] = useState<Internship[]>([]);
  const [candidates, setCandidates] = useState<TeamCandidate[]>([]);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [queue, setQueue] = useState<VerificationRequest[]>([]);
  const [totalStudentsCount, setTotalStudentsCount] = useState<number>(1);

  // Status & loading states
  const [isLoading, setIsLoading] = useState<boolean>(() => {
    return !!localStorage.getItem('skillbridge_auth_token');
  });
  const [apiError, setApiError] = useState<string | null>(null);

  // Modals & Toast state
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null);
  const [selectedMatchItem, setSelectedMatchItem] = useState<Internship | TeamCandidate | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [toastType, setToastType] = useState<'success' | 'info' | 'error'>('success');

  const showToast = (message: string, type: 'success' | 'info' | 'error' = 'success') => {
    setToastMessage(message);
    setToastType(type);
  };

  // Synchronize URL hash and browser history popstate (Chrome Back / Forward Navigation)
  useEffect(() => {
    const handlePopState = (event: PopStateEvent) => {
      if (event.state && event.state.screen) {
        setCurrentScreen(event.state.screen);
      } else {
        const hash = window.location.hash.replace('#/', '').trim();
        if (hash && VALID_SCREENS.includes(hash as ScreenType)) {
          setCurrentScreen(hash as ScreenType);
        }
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Update URL hash whenever currentScreen changes
  useEffect(() => {
    if (window.location.hash !== `#/${currentScreen}`) {
      window.history.replaceState({ screen: currentScreen }, '', `#/${currentScreen}`);
    }
  }, [currentScreen]);

  // Convert backend Student data into UI formats
  const processStudentData = (studentData: ApiStudent) => {
    setStudent(studentData);

    // Convert student skills list into UI Skill format
    if (studentData.skills) {
      const mappedSkills: Skill[] = studentData.skills.map((ss) => {
        const skillName = ss.skill?.name || `Skill #${ss.skill_id}`;
        const category = ss.skill?.category || 'Programming';
        const isVerified = ss.verification_status === 'verified';
        
        // Count verified evidence for this skill (checking both direct skill_id and many-to-many skills association)
        const relatedEvCount = (studentData.evidence || []).filter(
          (e) =>
            e.verification_status === 'verified' &&
            (e.skill_id === ss.skill_id ||
              (e.skills && e.skills.some((sk) => sk.id === ss.skill_id)))
        ).length;

        let percentage = 84;
        if (relatedEvCount >= 3) percentage = 96;
        else if (relatedEvCount === 2) percentage = 92;
        else if (relatedEvCount === 1) percentage = 84;
        else if (ss.proficiency_level?.toLowerCase() === 'advanced') percentage = 92;
        else if (ss.proficiency_level?.toLowerCase() === 'intermediate') percentage = 84;
        else percentage = 75;

        return {
          id: `skill-${ss.id}`,
          apiId: ss.skill_id,
          name: skillName,
          category,
          level: (ss.proficiency_level as any) || 'Intermediate',
          percentage,
          evidenceCount: relatedEvCount > 0 ? relatedEvCount : 1,
          verifiedByAi: isVerified,
          evidenceIds: (studentData.evidence || [])
            .filter(
              (e) =>
                e.skill_id === ss.skill_id ||
                (e.skills && e.skills.some((sk) => sk.id === ss.skill_id))
            )
            .map((e) => `ev-${e.id}`),
        };
      });
      setSkills(mappedSkills);
    } else {
      setSkills([]);
    }

    // Convert evidence list with multi-skill normalization
    if (studentData.evidence) {
      const mappedEvidence: EvidenceItem[] = studentData.evidence.map((ev) => {
        const typeCapitalized = ev.evidence_type.charAt(0).toUpperCase() + ev.evidence_type.slice(1);
        const allSkillNames =
          ev.skills && ev.skills.length > 0
            ? ev.skills.map((s) => s.name)
            : ev.skill?.name
            ? [ev.skill.name]
            : ['General Engineering'];

        return {
          id: `ev-${ev.id}`,
          apiId: ev.id,
          title: ev.title,
          type: typeCapitalized,
          institution: ev.issuer || 'SkillBridge Verification Protocol',
          skills: allSkillNames,
          date: ev.created_at ? ev.created_at.slice(0, 10) : new Date().toISOString().slice(0, 10),
          verificationStatus: (ev.verification_status as any) || 'pending',
          score: 95,
          fileName: `${ev.title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_record.pdf`,
          url: ev.evidence_url || undefined,
          aiFeedback: ev.description || 'Submitted artifact for Skill Passport evaluation.',
        };
      });
      setEvidenceList(mappedEvidence);
    } else {
      setEvidenceList([]);
    }
  };

  // Convert backend recommendations into UI Internship format with explainability
  const processRecommendations = (recommendations: ApiRecommendation[]) => {
    const mappedInternships: Internship[] = recommendations.map((rec, index) => {
      const isTopMatch = index === 0 && rec.match_score >= 80;
      const logo = LOGO_MAP[rec.company] || DEFAULT_LOGO;

      return {
        id: `internship-${rec.internship_id}`,
        apiId: rec.internship_id,
        title: rec.internship_title,
        company: rec.company,
        logo,
        location: rec.location,
        type: rec.location.toLowerCase().includes('remote') ? 'Remote' : 'Hybrid',
        employmentType: 'Internship',
        matchPercentage: Math.round(rec.match_score),
        isTopMatch,
        postedDate: 'Active',
        verifiedSkills: rec.matched_skills.map((ms) => ms.skill_name),
        missingSkills: rec.missing_skills,
        description: rec.description,
        applied: false,
        explanation: rec.explanation,
        matchedSkillsDetails: rec.matched_skills,
        supportingEvidence: rec.evidence_support,
        requiredSkillsList: rec.required_skills,
        preferredSkillsList: rec.preferred_skills,
      };
    });
    setInternships(mappedInternships);
  };

  // Process activities from backend API
  const processActivities = (apiActivities: ApiActivity[]) => {
    const mapped: ActivityItem[] = apiActivities.map((act) => {
      let icon = act.icon || 'notifications';
      let type: 'verification' | 'match' | 'team' | 'team_invitation' = 'verification';

      if (act.activity_type === 'team' || act.activity_type === 'team_invitation') {
        type = 'team';
        icon = 'person_add';
      } else if (act.activity_type === 'match' || act.activity_type === 'application') {
        type = 'match';
        icon = 'stars';
      } else if (act.activity_type === 'verification' || act.activity_type === 'evidence_submitted') {
        type = 'verification';
        icon = 'check_circle';
      }

      return {
        id: `act-${act.id}`,
        title: act.title,
        subtitle: act.description || 'Verified via SkillBridge Engine',
        time: act.created_at ? act.created_at.slice(0, 10) : 'Recent',
        icon,
        type,
        isRead: act.is_read,
        relatedEntityType: act.related_entity_type || undefined,
        relatedEntityId: act.related_entity_id || undefined,
      };
    });
    setActivities(mapped);
  };

  // Convert backend candidate recommendations into UI TeamCandidate view models
  const processTeamCandidates = (recs: ApiTeamCandidateRecommendation[], invitedStudentIds: Set<number>) => {
    const mapped: TeamCandidate[] = recs.map((rec, index) => {
      const avatar = AVATAR_LIST[index % AVATAR_LIST.length];
      const isInvited = invitedStudentIds.has(rec.candidate_id);

      const allCandidateSkills = rec.verified_skills && rec.verified_skills.length > 0
        ? rec.verified_skills
        : Array.from(new Set([
            ...(rec.skills_contributed || []),
            ...(rec.complementary_skills || []),
            ...(rec.matched_skills || []).map((ms) => ms.skill_name),
          ]));

      return {
        id: `candidate-${rec.candidate_id}`,
        name: rec.candidate_name,
        role: rec.professional_role || rec.role_suggestion,
        level: rec.overall_proficiency || 'Intermediate',
        avatar,
        matchPercentage: Math.round(rec.match_score),
        aiInsight: rec.explanation,
        verifiedSkills: allCandidateSkills,
        skillsContributed: rec.skills_contributed || [],
        complementarySkills: rec.complementary_skills || [],
        missingSkills: rec.missing_team_skills || [],
        invited: isInvited,
        education: rec.university || 'SkillBridge Academic Network',
        location: 'Verified Student Network',
        matchedSkillsDetails: rec.matched_skills,
        professionalRole: rec.professional_role,
        verifiedDomains: rec.verified_domains,
        targetRole: rec.target_role,
        evidenceBreakdown: rec.evidence_breakdown,
        coreSkillsFulfilled: rec.core_skills_fulfilled || [],
        coreSkillsMissing: rec.core_skills_missing || [],
      };
    });
    setCandidates(mapped);
  };

  // Main data loader connected to live backend & Neon DB
  const loadBackendData = useCallback(async (targetStudentId?: number) => {
    setIsLoading(true);
    setApiError(null);

    try {
      // 1. Fetch current authenticated student profile
      const studentData = await studentsApi.getMyProfile();
      setActiveStudentId(studentData.id);
      processStudentData(studentData);

      // 2. Fetch explainable internship recommendations
      try {
        const recData = await recommendationsApi.getMyRecommendations();
        if (recData && recData.recommendations) {
          processRecommendations(recData.recommendations);
        }
      } catch (recErr) {
        try {
          const rawInternships = await internshipsApi.getInternships();
          const mappedFallback: Internship[] = (rawInternships || []).map((raw) => ({
            id: `internship-${raw.id}`,
            apiId: raw.id,
            title: raw.title,
            company: raw.company,
            logo: LOGO_MAP[raw.company] || DEFAULT_LOGO,
            location: raw.location,
            type: raw.location.toLowerCase().includes('remote') ? 'Remote' : 'Hybrid',
            employmentType: 'Internship',
            matchPercentage: 75,
            postedDate: 'Active',
            verifiedSkills: raw.required_skills || [],
            description: raw.description,
            applied: false,
          }));
          setInternships(mappedFallback);
        } catch {
          // Fallback to empty if not available
        }
      }

      // 3. Fetch evidence verification queue (Admin queue)
      try {
        const allEv = await evidenceApi.getAllEvidence();
        const mappedQueue: VerificationRequest[] = allEv.map((ev) => {
          const allSkills =
            ev.skills && ev.skills.length > 0
              ? ev.skills.map((s) => s.name)
              : ev.skill?.name
              ? [ev.skill.name]
              : ['Technical Competency'];

          return {
            id: `vq-${ev.id}`,
            apiId: ev.id,
            studentName:
              ev.student?.name ||
              (ev.student_id === studentData.id ? studentData.name : `Student #${ev.student_id}`),
            studentInitials: (ev.student?.name || studentData.name || 'ST')
              .split(' ')
              .map((w) => w[0])
              .join('')
              .slice(0, 2)
              .toUpperCase(),
            title: ev.title,
            type: ev.evidence_type.charAt(0).toUpperCase() + ev.evidence_type.slice(1),
            submittedTime: ev.created_at ? ev.created_at.slice(0, 10) : 'Recent',
            skills: allSkills,
            status:
              ev.verification_status === 'verified'
                ? 'approved'
                : ev.verification_status === 'rejected'
                ? 'rejected'
                : 'pending',
            evidenceSnippet: ev.description || 'Artifact submitted for evaluation.',
            evidenceUrl: ev.evidence_url || undefined,
          };
        });
        setQueue(mappedQueue);
      } catch {
        // Ignore queue failure
      }

      // 4. Fetch persistent activities from backend DB
      try {
        const apiActs = await activitiesApi.getActivities(studentData.id);
        processActivities(apiActs);
      } catch {
        // Fallback
      }

      // 5. Fetch Team Builder Teams & Candidate Recommendations from Backend DB
      try {
        let userTeams = await teamsApi.getMyTeams();
        let currentTeam = userTeams && userTeams.length > 0 ? userTeams[0] : null;
        if (!currentTeam) {
          let existingTeams = await teamsApi.getTeams();
          currentTeam = existingTeams && existingTeams.length > 0 ? existingTeams[0] : null;
        }

        if (!currentTeam) {
          currentTeam = await teamsApi.createTeam({
            name: 'Hex Bridge',
            project_name: 'AI & Full Stack Collaborative Platform',
            description: 'Multidisciplinary engineering team for hackathons and projects.',
            creator_id: studentData.id,
            required_domains: ['Frontend', 'Backend', 'Database', 'AI/ML', 'UI/UX'],
          });
        }

        setActiveTeam(currentTeam);
        setActiveTeamId(currentTeam.id);

        const invitedIds = new Set<number>();
        (currentTeam.members || []).forEach((m) => {
          if (m.student_id !== studentData.id) {
            invitedIds.add(m.student_id);
          }
        });
        (currentTeam.invitations || []).forEach((inv) => {
          if (inv.status === 'PENDING') {
            invitedIds.add(inv.recipient_id);
          }
        });

        const candRecs = await teamsApi.getTeamCandidates(currentTeam.id);
        processTeamCandidates(candRecs, invitedIds);
      } catch {
        // Ignore team failure
      }

      // 6. Fetch total students count
      try {
        const allStudents = await studentsApi.getStudents();
        setTotalStudentsCount(allStudents.length);
      } catch {
        setTotalStudentsCount(1);
      }

      setIsLoading(false);
    } catch (err: any) {
      setIsLoading(false);
      if (err.status === 401 || err.status === 403 || err.status === 404) {
        localStorage.removeItem('skillbridge_auth_token');
        localStorage.removeItem('skillbridge_student_id');
        localStorage.removeItem('skillbridge_student_name');
        localStorage.removeItem('skillbridge_last_screen');
        setAuthToken(null);
        setActiveStudentId(null);
        setStudent(null);
        setCurrentScreen('login');
        showToast('Your session has expired. Please sign in or create an account to continue.', 'info');
      } else {
        setApiError(
          err.message ||
            'Unable to connect to the backend server. Please verify FastAPI is running.'
        );
      }
    }
  }, []);

  useEffect(() => {
    if (authToken) {
      loadBackendData(activeStudentId || undefined);
    } else {
      setIsLoading(false);
    }
  }, [loadBackendData, activeStudentId, authToken]);

  // Navigation handler with HTML5 History and persistent screen state
  const handleNavigate = (screen: ScreenType) => {
    if (screen === 'admin' && !adminToken) {
      screen = 'admin-login';
    }
    window.history.pushState({ screen }, '', `#/${screen}`);
    setCurrentScreen(screen);
    if (screen !== 'login' && screen !== 'admin-login') {
      localStorage.setItem('skillbridge_last_screen', screen);
      studentsApi.updateMyState(screen).catch(() => {});
    }
  };

  // Login Success Handler
  const handleLoginSuccess = async (authData: ApiStudentLoginResponse) => {
    const studentId = authData.student.id;
    setAuthToken(authData.token);
    setActiveStudentId(studentId);
    localStorage.setItem('skillbridge_auth_token', authData.token);
    localStorage.setItem('skillbridge_student_id', String(studentId));
    localStorage.setItem('skillbridge_student_name', authData.student.name);

    // Resume exact screen where user last discontinued
    const backendScreen = authData.last_screen as ScreenType;
    const localScreen = localStorage.getItem('skillbridge_last_screen') as ScreenType;
    const resumeScreen =
      backendScreen && backendScreen !== 'login'
        ? backendScreen
        : localScreen && localScreen !== 'login'
        ? localScreen
        : 'dashboard';

    localStorage.setItem('skillbridge_last_screen', resumeScreen);
    window.history.pushState({ screen: resumeScreen }, '', `#/${resumeScreen}`);
    setCurrentScreen(resumeScreen);

    await loadBackendData(studentId);
    showToast(authData.message || `Welcome back, ${authData.student.name}!`);
  };

  // Logout Handler
  const handleLogout = () => {
    localStorage.removeItem('skillbridge_auth_token');
    localStorage.removeItem('skillbridge_student_id');
    localStorage.removeItem('skillbridge_student_name');
    localStorage.removeItem('skillbridge_last_screen');
    setAuthToken(null);
    setActiveStudentId(null);
    setStudent(null);
    setSkills([]);
    setEvidenceList([]);
    setInternships([]);
    setCandidates([]);
    setActivities([]);
    window.history.pushState({ screen: 'login' }, '', '#/login');
    setCurrentScreen('login');
    showToast('Logged out successfully.', 'info');
  };

  // Handler: Add new evidence (Status: PENDING)
  const handleAddEvidence = async (
    newEvidenceData: Omit<EvidenceItem, 'id' | 'date' | 'verificationStatus'>,
    backendEvidenceId?: number
  ) => {
    const newId = backendEvidenceId ? `ev-${backendEvidenceId}` : `ev-${Date.now()}`;
    const dateStr = new Date().toISOString().slice(0, 10);
    
    const newEvidence: EvidenceItem = {
      id: newId,
      apiId: backendEvidenceId,
      ...newEvidenceData,
      date: dateStr,
      verificationStatus: 'pending',
    };

    setEvidenceList((prev) => [newEvidence, ...prev]);
    await loadBackendData();
    showToast(`Evidence "${newEvidenceData.title}" submitted. Status: PENDING VERIFICATION.`);
  };

  // Handler: Apply for Internship
  const handleApplyInternship = async (internshipId: string) => {
    setInternships(
      internships.map((item) => {
        if (item.id === internshipId) {
          return { ...item, applied: true };
        }
        return item;
      })
    );

    const appliedItem = internships.find((i) => i.id === internshipId);
    if (appliedItem && activeStudentId) {
      try {
        await activitiesApi.createActivity({
          student_id: activeStudentId,
          activity_type: 'application',
          title: `Applied to ${appliedItem.title}`,
          description: `${appliedItem.company} • Submitted with Verifiable Skill Passport`,
          icon: 'stars',
          related_entity_type: 'internship',
          related_entity_id: appliedItem.apiId,
        });

        const freshActivities = await activitiesApi.getActivities(activeStudentId);
        processActivities(freshActivities);
      } catch {
        // Fallback
      }

      showToast(`Application with Digital Skill Passport submitted to ${appliedItem.company}!`);
    }
  };

  // Handler: Invite Team Candidate with persistent backend invitation
  const handleInviteCandidate = async (candidateIdStr: string) => {
    const candidateId = parseInt(candidateIdStr.replace('candidate-', ''), 10);

    setCandidates(
      candidates.map((item) => {
        if (item.id === candidateIdStr) {
          return { ...item, invited: true };
        }
        return item;
      })
    );

    const invitedCand = candidates.find((c) => c.id === candidateIdStr);

    if (activeTeamId && !isNaN(candidateId)) {
      try {
        await teamsApi.createTeamInvitation(activeTeamId, {
          recipient_id: candidateId,
          role: invitedCand?.role || 'Team Member',
          message: `Join our team on ${selectedEvidence?.title || 'SkillBridge Project'}`,
        });

        if (activeStudentId) {
          await loadBackendData(activeStudentId);
        }
      } catch {
        // Optimistic fallback
      }
    }

    if (invitedCand) {
      showToast(`Team invitation successfully sent to ${invitedCand.name}!`);
    }
  };

  // Handler: Admin approve evidence
  const handleApproveQueue = async (id: string, apiId?: number) => {
    if (apiId) {
      try {
        await adminApi.approveEvidence(apiId);
        if (activeStudentId) {
          await loadBackendData(activeStudentId);
        }
        showToast('Evidence approved! All verified skills indexed into student passport.');
      } catch (err: any) {
        showToast(err.message || 'Failed to approve evidence.', 'error');
      }
    }
    setQueue(queue.map((q) => (q.id === id ? { ...q, status: 'approved' } : q)));
  };

  // Handler: Admin reject evidence
  const handleRejectQueue = async (id: string, apiId?: number) => {
    if (apiId) {
      try {
        await adminApi.rejectEvidence(apiId);
        if (activeStudentId) {
          await loadBackendData(activeStudentId);
        }
        showToast('Evidence rejected / flagged for student resubmission.', 'info');
      } catch (err: any) {
        showToast(err.message || 'Failed to reject evidence.', 'error');
      }
    }
    setQueue(queue.map((q) => (q.id === id ? { ...q, status: 'rejected' } : q)));
  };

  const handleViewSnippet = (req: VerificationRequest) => {
    setSelectedEvidence({
      id: req.id,
      title: req.title,
      type: req.type,
      institution: 'Submitted by ' + req.studentName,
      skills: req.skills,
      date: req.submittedTime,
      verificationStatus:
        req.status === 'approved' ? 'verified' : req.status === 'rejected' ? 'rejected' : 'pending',
      score: 95,
      fileName: `${req.title.toLowerCase().replace(/[^a-z0-9]/g, '_')}.pdf`,
      url: req.evidenceUrl,
      aiFeedback: req.evidenceSnippet || 'Verification record submitted for evaluation.',
    });
  };

  const verifiedSkillsCount = skills.filter((s) => s.verifiedByAi).length;
  const verifiedEvidenceCount = evidenceList.filter((e) => e.verificationStatus === 'verified').length;
  const pendingEvidenceCount = evidenceList.filter((e) => e.verificationStatus === 'pending').length;
  const pendingQueueCount = queue.filter((q) => q.status === 'pending').length;

  const completionPercentage = Math.min(100, verifiedSkillsCount * 20);

  // If user is not authenticated or explicitly on login screen, render LoginView
  if (currentScreen === 'login' || !authToken) {
    return (
      <div className="min-h-screen bg-[#f7f9fb] text-[#191c1e] flex flex-col font-['Inter',sans-serif]">
        <LoginView onLoginSuccess={handleLoginSuccess} />
        <Toast
          message={toastMessage}
          type={toastType}
          onClose={() => setToastMessage(null)}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f7f9fb] text-[#191c1e] flex flex-col font-['Inter',sans-serif]">
      {/* Top Navbar with Notification Center */}
      <Navbar
        currentScreen={currentScreen}
        onNavigate={handleNavigate}
        pendingCount={pendingQueueCount}
        studentName={student?.name || 'Student'}
        studentId={activeStudentId || undefined}
        onSwitchStudent={handleLogout}
        onLogout={handleLogout}
        isAdminAuthenticated={!!adminToken}
        onInvitationAction={() => loadBackendData(activeStudentId || undefined)}
      />

      {/* Screen Render */}
      <div className="flex-1">
        {currentScreen === 'landing' && (
          <LandingView onNavigate={handleNavigate} />
        )}

        {currentScreen === 'passport' && (
          <PassportView
            skills={skills}
            evidenceList={evidenceList}
            isLoading={isLoading}
            error={apiError}
            onRetry={() => loadBackendData()}
            onNavigate={handleNavigate}
            onOpenEvidence={setSelectedEvidence}
          />
        )}

        {currentScreen === 'dashboard' && (
          <StudentDashboardView
            studentName={student?.name || 'Student'}
            internships={internships}
            activities={activities}
            verifiedSkillsCount={verifiedSkillsCount}
            evidenceItemsCount={evidenceList.length}
            pendingEvidenceCount={pendingEvidenceCount}
            verifiedEvidenceCount={verifiedEvidenceCount}
            completionPercentage={completionPercentage}
            isLoading={isLoading}
            error={apiError}
            onRetry={() => loadBackendData()}
            onNavigate={handleNavigate}
            onSelectInternship={(internship) => {
              setSelectedMatchItem(internship);
            }}
          />
        )}

        {currentScreen === 'internships' && (
          <InternshipsView
            internships={internships}
            isLoading={isLoading}
            error={apiError}
            onRetry={() => loadBackendData()}
            onApply={handleApplyInternship}
            onOpenMatchModal={setSelectedMatchItem}
            onNavigate={handleNavigate}
          />
        )}

        {currentScreen === 'team-builder' && (
          <TeamBuilderView
            studentName={student?.name || 'Student'}
            candidates={candidates}
            teamId={activeTeamId || 1}
            activeTeam={activeTeam}
            initialRoleFilter={teamRoleFilter}
            isLoading={isLoading}
            error={apiError}
            onRetry={() => loadBackendData()}
            onInviteCandidate={handleInviteCandidate}
            onOpenMatchModal={setSelectedMatchItem}
            onNavigate={handleNavigate}
          />
        )}

        {currentScreen === 'my-team' && (
          <MyTeamView
            studentName={student?.name || 'Student'}
            studentId={student?.id || activeStudentId || 1}
            onNavigate={handleNavigate}
            onSelectMissingDomain={(domain) => {
              const dLower = domain.toLowerCase();
              if (dLower.includes('frontend')) setTeamRoleFilter('Frontend Developer');
              else if (dLower.includes('backend')) setTeamRoleFilter('Backend Developer');
              else if (dLower.includes('ai') || dLower.includes('ml')) setTeamRoleFilter('AI/ML Developer');
              else if (dLower.includes('data') || dLower.includes('sql') || dLower.includes('database')) setTeamRoleFilter('Database Specialist');
              else if (dLower.includes('ui') || dLower.includes('ux') || dLower.includes('design')) setTeamRoleFilter('UI/UX Designer');
              else if (dLower.includes('devops') || dLower.includes('cloud')) setTeamRoleFilter('DevOps Engineer');
              else if (dLower.includes('full stack')) setTeamRoleFilter('Full Stack Developer');
              else setTeamRoleFilter('All');
            }}
          />
        )}

        {currentScreen === 'add-evidence' && (
          <AddEvidenceView
            studentId={student?.id || activeStudentId || undefined}
            onAddEvidence={handleAddEvidence}
            onNavigate={handleNavigate}
          />
        )}

        {currentScreen === 'admin-login' && (
          <AdminLoginView
            onLoginSuccess={() => {
              setAdminToken(localStorage.getItem('skillbridge_admin_token'));
              handleNavigate('admin');
              showToast('Admin logged in successfully!');
            }}
            onNavigate={handleNavigate}
          />
        )}

        {currentScreen === 'admin' && (
          <AdminDashboardView
            queue={queue}
            totalStudentsCount={totalStudentsCount}
            activeInternshipsCount={internships.length}
            isLoading={isLoading}
            onApprove={handleApproveQueue}
            onReject={handleRejectQueue}
            onNavigate={handleNavigate}
            onViewSnippet={handleViewSnippet}
            onLogout={() => {
              localStorage.removeItem('skillbridge_admin_token');
              setAdminToken(null);
              handleNavigate('dashboard');
              showToast('Admin logged out.');
            }}
          />
        )}
      </div>

      {/* Shared Mobile Bottom Navigation */}
      <BottomNav
        currentScreen={currentScreen}
        onNavigate={handleNavigate}
      />

      {/* Reusable Modals */}
      <EvidenceModal
        isOpen={!!selectedEvidence}
        evidence={selectedEvidence}
        onClose={() => setSelectedEvidence(null)}
      />

      <MatchModal
        isOpen={!!selectedMatchItem}
        item={selectedMatchItem}
        onClose={() => setSelectedMatchItem(null)}
        onApplyOrInvite={() => {
          if (selectedMatchItem) {
            if ('company' in selectedMatchItem) {
              handleApplyInternship((selectedMatchItem as Internship).id);
            } else {
              handleInviteCandidate((selectedMatchItem as TeamCandidate).id);
            }
          }
        }}
      />

      {/* Toast Notification */}
      <Toast
        message={toastMessage}
        type={toastType}
        onClose={() => setToastMessage(null)}
      />
    </div>
  );
}
