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
} from './types';
import {
  studentsApi,
  recommendationsApi,
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

export default function App() {
  const [authToken, setAuthToken] = useState<string | null>(() => {
    return localStorage.getItem('skillbridge_auth_token');
  });
  const [activeStudentId, setActiveStudentId] = useState<number | null>(() => {
    const saved = localStorage.getItem('skillbridge_student_id');
    return saved ? Number(saved) : null;
  });
  const [currentScreen, setCurrentScreen] = useState<ScreenType>(() => {
    const token = localStorage.getItem('skillbridge_auth_token');
    if (!token) return 'login';
    const savedScreen = localStorage.getItem('skillbridge_last_screen') as ScreenType;
    return savedScreen && savedScreen !== 'login' ? savedScreen : 'dashboard';
  });
  const [adminToken, setAdminToken] = useState<string | null>(() => {
    return localStorage.getItem('skillbridge_admin_token');
  });
  const [activeTeamId, setActiveTeamId] = useState<number | null>(null);
  
  // App state backed by live FastAPI backend
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
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  // Convert backend student skills & evidence into frontend view models
  const processStudentData = (studentData: ApiStudent) => {
    setStudent(studentData);

    // Convert skills
    if (studentData.skills) {
      const verifiedStudentSkills = studentData.skills.filter(s => s.verification_status === 'verified');
      const mappedSkills: Skill[] = verifiedStudentSkills.map((ss) => {
        const skillName = ss.skill?.name || `Skill #${ss.skill_id}`;
        const category = ss.skill?.category || 'Programming';
        const isVerified = ss.verification_status === 'verified';
        
        // Dynamic proficiency formula: 1 verified = 84%, 2 = 92%, 3 = 96%, 4+ = 99%
        const relatedEvCount = (studentData.evidence || []).filter(
          e => e.skill_id === ss.skill_id && e.verification_status === 'verified'
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
          evidenceIds: (studentData.evidence || []).filter(e => e.skill_id === ss.skill_id).map(e => `ev-${e.id}`),
        };
      });
      setSkills(mappedSkills);
    } else {
      setSkills([]);
    }

    // Convert evidence list
    if (studentData.evidence) {
      const mappedEvidence: EvidenceItem[] = studentData.evidence.map((ev) => {
        const typeCapitalized = ev.evidence_type.charAt(0).toUpperCase() + ev.evidence_type.slice(1);
        const skillName = ev.skill?.name;

        return {
          id: `ev-${ev.id}`,
          apiId: ev.id,
          title: ev.title,
          type: typeCapitalized,
          institution: ev.issuer || 'SkillBridge Verification Protocol',
          skills: skillName ? [skillName] : ['General Engineering'],
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
        verifiedSkills: rec.matched_skills.map(ms => ms.skill_name),
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
      let type: 'verification' | 'match' | 'team' = 'verification';

      if (act.activity_type === 'team') {
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
      };
    });
    setActivities(mapped);
  };

  // Convert backend candidate recommendations into UI TeamCandidate view models
  const processTeamCandidates = (recs: ApiTeamCandidateRecommendation[], invitedStudentIds: Set<number>) => {
    const mapped: TeamCandidate[] = recs.map((rec, index) => {
      const avatar = AVATAR_LIST[index % AVATAR_LIST.length];
      const isInvited = invitedStudentIds.has(rec.candidate_id);

      return {
        id: `candidate-${rec.candidate_id}`,
        name: rec.candidate_name,
        role: rec.role_suggestion,
        level: 'Verified Skill Passport',
        avatar,
        matchPercentage: Math.round(rec.match_score),
        aiInsight: rec.explanation,
        verifiedSkills: rec.skills_contributed.length > 0 ? rec.skills_contributed : ['General Engineering'],
        invited: isInvited,
        education: rec.university || 'Verified Academic Credentials',
        location: 'Verified Student Passport',
        missingSkills: rec.missing_team_skills,
        matchedSkillsDetails: rec.matched_skills,
      };
    });
    setCandidates(mapped);
  };

  // Fetch all initial data from FastAPI backend
  const loadBackendData = useCallback(async (targetStudentId: number) => {
    setIsLoading(true);
    setApiError(null);

    try {
      // 1. Fetch Student Profile & Passport Data
      const studentData = await studentsApi.getStudent(targetStudentId);
      processStudentData(studentData);

      // 2. Fetch Live Internship Recommendations
      try {
        const recsResponse = await recommendationsApi.getStudentRecommendations(targetStudentId);
        if (recsResponse && recsResponse.recommendations) {
          processRecommendations(recsResponse.recommendations);
        }
      } catch {
        // If student has 0 skills or recommendation fails
        setInternships([]);
      }

      // 3. Fetch Evidence Queue for Admin Dashboard
      try {
        const allEv = await evidenceApi.getAllEvidence();
        const mappedQueue: VerificationRequest[] = allEv.map((ev) => ({
          id: `vq-${ev.id}`,
          apiId: ev.id,
          studentName: ev.student?.name || (ev.student_id === targetStudentId ? studentData.name : `Student #${ev.student_id}`),
          studentInitials: ((ev.student?.name || studentData.name || 'ST').split(' ').map(w => w[0]).join('').slice(0, 2)).toUpperCase(),
          title: ev.title,
          type: ev.evidence_type.charAt(0).toUpperCase() + ev.evidence_type.slice(1),
          submittedTime: ev.created_at ? ev.created_at.slice(0, 10) : 'Recent',
          skills: ev.skill ? [ev.skill.name] : ['Technical Competency'],
          status: ev.verification_status === 'verified' ? 'approved' : ev.verification_status === 'rejected' ? 'rejected' : 'pending',
          evidenceSnippet: ev.description || 'Artifact submitted for evaluation.',
          evidenceUrl: ev.evidence_url || undefined,
        }));
        setQueue(mappedQueue);
      } catch {
        // Ignore queue failure
      }

      // 4. Fetch persistent activities from backend DB
      try {
        const apiActs = await activitiesApi.getActivities(targetStudentId);
        processActivities(apiActs);
      } catch {
        // Fallback
      }

      // 5. Fetch Team Builder Teams & Candidate Recommendations from Backend DB
      try {
        let existingTeams = await teamsApi.getTeams();
        let currentTeam = existingTeams.length > 0 ? existingTeams[0] : null;

        if (!currentTeam) {
          currentTeam = await teamsApi.createTeam({
            name: 'AI & UX Research Project',
            description: 'Multidisciplinary AI, UI/UX, and Backend engineering team.',
            creator_id: targetStudentId,
            required_skill_ids: [1, 2, 5], // Python, React, Machine Learning
          });
        }

        setActiveTeamId(currentTeam.id);

        const invitedIds = new Set<number>();
        (currentTeam.members || []).forEach(m => {
          if (m.student_id !== targetStudentId) {
            invitedIds.add(m.student_id);
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
      setApiError(err.message || 'Unable to connect to the backend server. Please verify FastAPI is running at http://127.0.0.1:8000.');
    }
  }, []);

  useEffect(() => {
    if (activeStudentId && authToken) {
      loadBackendData(activeStudentId);
    } else {
      setIsLoading(false);
    }
  }, [loadBackendData, activeStudentId, authToken]);

  // Navigation handler that persists current screen to backend and localStorage
  const handleNavigate = (screen: ScreenType) => {
    if (screen === 'admin' && !adminToken) {
      setCurrentScreen('admin-login');
      return;
    }
    setCurrentScreen(screen);
    if (screen !== 'login' && screen !== 'admin-login') {
      localStorage.setItem('skillbridge_last_screen', screen);
      if (activeStudentId) {
        studentsApi.updateStudentState(activeStudentId, screen).catch(() => {});
      }
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
    const resumeScreen = (backendScreen && backendScreen !== 'login')
      ? backendScreen
      : (localScreen && localScreen !== 'login')
        ? localScreen
        : 'dashboard';

    localStorage.setItem('skillbridge_last_screen', resumeScreen);
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

    setEvidenceList([newEvidence, ...evidenceList]);
    if (activeStudentId) {
      await loadBackendData(activeStudentId);
    }
    showToast(`Evidence "${newEvidenceData.title}" submitted. Status: PENDING VERIFICATION.`);
  };

  // Handler: Apply for Internship
  const handleApplyInternship = async (internshipId: string) => {
    setInternships(internships.map(item => {
      if (item.id === internshipId) {
        return { ...item, applied: true };
      }
      return item;
    }));

    const appliedItem = internships.find(i => i.id === internshipId);
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

  // Handler: Invite Team Candidate
  const handleInviteCandidate = async (candidateIdStr: string) => {
    const candidateId = parseInt(candidateIdStr.replace('candidate-', ''), 10);

    setCandidates(candidates.map(item => {
      if (item.id === candidateIdStr) {
        return { ...item, invited: true };
      }
      return item;
    }));

    const invitedCand = candidates.find(c => c.id === candidateIdStr);

    if (activeTeamId && !isNaN(candidateId)) {
      try {
        await teamsApi.addTeamMember(activeTeamId, {
          student_id: candidateId,
          role: invitedCand?.role || 'Team Member',
          status: 'invited',
        });

        if (activeStudentId) {
          await loadBackendData(activeStudentId);
        }
      } catch {
        // Keep optimistic update
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
        showToast('Evidence approved! Verified competency added to student passport.');
      } catch (err: any) {
        showToast(err.message || 'Failed to approve evidence.', 'error');
      }
    }
    setQueue(queue.map(q => q.id === id ? { ...q, status: 'approved' } : q));
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
    setQueue(queue.map(q => q.id === id ? { ...q, status: 'rejected' } : q));
  };

  const handleViewSnippet = (req: VerificationRequest) => {
    setSelectedEvidence({
      id: req.id,
      title: req.title,
      type: req.type,
      institution: 'Submitted by ' + req.studentName,
      skills: req.skills,
      date: req.submittedTime,
      verificationStatus: req.status === 'approved' ? 'verified' : req.status === 'rejected' ? 'rejected' : 'pending',
      score: 95,
      fileName: `${req.title.toLowerCase().replace(/[^a-z0-9]/g, '_')}.pdf`,
      url: req.evidenceUrl,
      aiFeedback: req.evidenceSnippet || 'Verification record submitted for evaluation.'
    });
  };

  const verifiedSkillsCount = skills.filter(s => s.verifiedByAi).length;
  const verifiedEvidenceCount = evidenceList.filter(e => e.verificationStatus === 'verified').length;
  const pendingEvidenceCount = evidenceList.filter(e => e.verificationStatus === 'pending').length;
  const pendingQueueCount = queue.filter(q => q.status === 'pending').length;

  // Dynamic Passport completion percentage (0 skills = 0%, 1 = 20%, 2 = 40%, 3 = 60%, 4 = 80%, 5+ = 100%)
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
      {/* Top Navbar */}
      <Navbar
        currentScreen={currentScreen}
        onNavigate={handleNavigate}
        pendingCount={pendingQueueCount}
        studentName={student?.name || localStorage.getItem('skillbridge_student_name') || 'Student'}
        onSwitchStudent={handleLogout}
        onLogout={handleLogout}
        isAdminAuthenticated={!!adminToken}
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
            onRetry={() => activeStudentId && loadBackendData(activeStudentId)}
            onNavigate={handleNavigate}
            onOpenEvidence={setSelectedEvidence}
          />
        )}

        {currentScreen === 'dashboard' && (
          <StudentDashboardView
            studentName={student?.name || localStorage.getItem('skillbridge_student_name') || 'Student'}
            internships={internships}
            activities={activities}
            verifiedSkillsCount={verifiedSkillsCount}
            evidenceItemsCount={evidenceList.length}
            pendingEvidenceCount={pendingEvidenceCount}
            verifiedEvidenceCount={verifiedEvidenceCount}
            completionPercentage={completionPercentage}
            isLoading={isLoading}
            error={apiError}
            onRetry={() => activeStudentId && loadBackendData(activeStudentId)}
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
            onRetry={() => activeStudentId && loadBackendData(activeStudentId)}
            onApply={handleApplyInternship}
            onOpenMatchModal={setSelectedMatchItem}
            onNavigate={handleNavigate}
          />
        )}

        {currentScreen === 'team-builder' && (
          <TeamBuilderView
            studentName={student?.name || localStorage.getItem('skillbridge_student_name') || 'Student'}
            candidates={candidates}
            isLoading={isLoading}
            error={apiError}
            onRetry={() => activeStudentId && loadBackendData(activeStudentId)}
            onInviteCandidate={handleInviteCandidate}
            onOpenMatchModal={setSelectedMatchItem}
            onNavigate={handleNavigate}
          />
        )}

        {currentScreen === 'add-evidence' && (
          <AddEvidenceView
            studentId={activeStudentId || 1}
            onAddEvidence={handleAddEvidence}
            onNavigate={handleNavigate}
          />
        )}

        {currentScreen === 'admin-login' && (
          <AdminLoginView
            onLoginSuccess={() => {
              setAdminToken(localStorage.getItem('skillbridge_admin_token'));
              setCurrentScreen('admin');
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
              setCurrentScreen('dashboard');
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
