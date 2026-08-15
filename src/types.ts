export type ScreenType = 
  | 'landing' 
  | 'passport' 
  | 'dashboard' 
  | 'internships' 
  | 'team-builder' 
  | 'add-evidence' 
  | 'admin'
  | 'admin-login';

export type SkillCategory = 'Programming' | 'Data Science' | 'Design' | 'Soft Skills' | 'Tools' | 'Backend Development' | 'Frontend Development' | 'Databases' | 'AI / Data Science' | 'DevOps / Infrastructure' | 'Programming Languages';

export type SkillLevel = 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';

// ----------------------------------------------------
// BACKEND API SCHEMAS & DTO INTERFACES
// ----------------------------------------------------

export interface ApiHealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface ApiSkill {
  id: number;
  name: string;
  category: string;
  description?: string | null;
}

export interface ApiStudentSkill {
  id: number;
  student_id: number;
  skill_id: number;
  proficiency_level: string;
  verification_status: string;
  verified_at?: string | null;
  skill?: ApiSkill | null;
}

export interface ApiSupportingEvidence {
  id: number;
  title: string;
  evidence_type: string;
  issuer?: string | null;
  verification_status: string;
  evidence_url?: string | null;
}

export interface ApiEvidence {
  id: number;
  student_id: number;
  skill_id?: number | null;
  evidence_type: 'coursework' | 'project' | 'competition' | 'certificate' | 'internship' | string;
  title: string;
  description?: string | null;
  issuer?: string | null;
  verification_status: 'verified' | 'pending' | 'rejected' | string;
  evidence_url?: string | null;
  created_at?: string | null;
  skill?: ApiSkill | null;
}

export interface ApiInternshipSkill {
  id: number;
  internship_id: number;
  skill_id: number;
  required: boolean;
  minimum_proficiency: string;
  skill?: ApiSkill | null;
}

export interface ApiInternship {
  id: number;
  title: string;
  company: string;
  description: string;
  location: string;
  required_skills?: string[];
  preferred_skills?: string[];
  created_at?: string | null;
  internship_skills?: ApiInternshipSkill[];
}

export interface ApiMatchedSkill {
  skill_id: number;
  skill_name: string;
  student_proficiency: string;
  required_proficiency: string;
  is_required: boolean;
  supporting_evidence: ApiSupportingEvidence[];
}

export interface ApiInsufficientSkill {
  skill_id: number;
  skill_name: string;
  student_proficiency: string;
  required_proficiency: string;
  supporting_evidence: ApiSupportingEvidence[];
}

export interface ApiUnverifiedSkill {
  skill_id: number;
  skill_name: string;
  reason: string;
}

export interface ApiRecommendation {
  internship_id: number;
  internship_title: string;
  company: string;
  location: string;
  description: string;
  required_skills: string[];
  preferred_skills: string[];
  match_score: number;
  total_required_skills: number;
  satisfied_required_skills: number;
  matched_skills: ApiMatchedSkill[];
  missing_skills: string[];
  insufficient_skills: ApiInsufficientSkill[];
  unverified_skills: ApiUnverifiedSkill[];
  evidence_support: ApiSupportingEvidence[];
  explanation: string;
}

export interface ApiStudentRecommendationsResponse {
  student_id: number;
  student_name: string;
  total_recommendations: number;
  recommendations: ApiRecommendation[];
}

export interface ApiStudent {
  id: number;
  name: string;
  email: string;
  university: string;
  graduation_year: number;
  created_at?: string | null;
  skills?: ApiStudentSkill[];
  evidence?: ApiEvidence[];
}

export interface ApiTeamMember {
  id: number;
  team_id: number;
  student_id: number;
  role: string;
  status: 'invited' | 'joined' | 'declined' | string;
  joined_at?: string | null;
  created_at: string;
  student_name?: string | null;
}

export interface ApiTeamSkillRequirement {
  id: number;
  team_id: number;
  skill_id: number;
  minimum_proficiency: string;
  required: boolean;
  skill_name?: string | null;
}

export interface ApiTeam {
  id: number;
  name: string;
  description?: string | null;
  creator_id: number;
  creator_name?: string | null;
  created_at: string;
  members: ApiTeamMember[];
  required_skills: ApiTeamSkillRequirement[];
}

export interface ApiCandidateSkillContribution {
  skill_id: number;
  skill_name: string;
  student_proficiency: string;
  required_proficiency: string;
  is_required: boolean;
  supporting_evidence: ApiSupportingEvidence[];
}

export interface ApiTeamCandidateRecommendation {
  candidate_id: number;
  candidate_name: string;
  university?: string | null;
  role_suggestion: string;
  match_score: number;
  matched_skills: ApiCandidateSkillContribution[];
  skills_contributed: string[];
  missing_team_skills: string[];
  explanation: string;
}

export interface ApiActivity {
  id: number;
  student_id?: number | null;
  activity_type: string;
  title: string;
  description?: string | null;
  icon?: string | null;
  related_entity_type?: string | null;
  related_entity_id?: number | null;
  is_read: boolean;
  created_at: string;
}


// ----------------------------------------------------
// UI VIEW MODEL TYPES (ADAPTERS & HELPERS)
// ----------------------------------------------------

export interface EvidenceItem {
  id: string;
  title: string;
  type: 'Coursework' | 'Project' | 'Competition' | 'Certificate' | 'Micro-credential' | string;
  institution: string;
  skills: string[];
  date: string;
  verificationStatus: 'verified' | 'pending' | 'rejected';
  score?: number;
  fileName?: string;
  aiFeedback?: string;
  url?: string;
  apiId?: number;
}

export interface Skill {
  id: string;
  name: string;
  category: SkillCategory | string;
  level: SkillLevel;
  percentage: number;
  evidenceCount: number;
  verifiedByAi: boolean;
  color?: string;
  evidenceIds: string[];
  apiId?: number;
}

export interface Internship {
  id: string;
  apiId?: number;
  title: string;
  company: string;
  logo: string;
  location: string;
  type: 'Remote' | 'Hybrid' | 'On-site' | string;
  employmentType: 'Full-time' | 'Part-time' | 'Internship' | string;
  matchPercentage: number;
  isTopMatch?: boolean;
  postedDate: string;
  verifiedSkills: string[];
  missingSkills?: string[];
  description: string;
  applied?: boolean;
  // Deep explainability fields
  explanation?: string;
  matchedSkillsDetails?: ApiMatchedSkill[];
  supportingEvidence?: ApiSupportingEvidence[];
  requiredSkillsList?: string[];
  preferredSkillsList?: string[];
}

export interface TeamCandidate {
  id: string;
  name: string;
  role: string;
  level: string;
  avatar: string;
  matchPercentage: number;
  aiInsight: string;
  verifiedSkills: string[];
  invited?: boolean;
  education: string;
  location: string;
  missingSkills?: string[];
  matchedSkillsDetails?: ApiCandidateSkillContribution[];
}

export interface VerificationRequest {
  id: string;
  apiId?: number;
  studentName: string;
  studentInitials: string;
  title: string;
  type: string;
  submittedTime: string;
  skills: string[];
  status: 'pending' | 'approved' | 'rejected';
  evidenceSnippet?: string;
  evidenceUrl?: string;
}

export interface ActivityItem {
  id: string;
  title: string;
  subtitle: string;
  time: string;
  icon: string;
  type: 'verification' | 'match' | 'team';
}
