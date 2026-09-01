import React, { useState, useEffect } from 'react';
import { EvidenceItem, ScreenType, ApiSkill } from '../types';
import { skillsApi, evidenceApi } from '../api';
import { SearchableSkillSelect } from '../components/common/SearchableSkillSelect';

type SimplifiedCategory = 'Project' | 'Competition' | 'Certificate' | 'Internship';

interface AddEvidenceViewProps {
  studentId?: number;
  onAddEvidence: (newEvidence: Omit<EvidenceItem, 'id' | 'date' | 'verificationStatus'>, backendEvidenceId?: number) => void;
  onNavigate: (screen: ScreenType) => void;
}

export const AddEvidenceView: React.FC<AddEvidenceViewProps> = ({
  studentId,
  onAddEvidence,
  onNavigate,
}) => {
  // Category state
  const [category, setCategory] = useState<SimplifiedCategory>('Project');

  // Project-specific fields
  const [projectName, setProjectName] = useState('');
  const [projectLink, setProjectLink] = useState('');
  const [projectDesc, setProjectDesc] = useState('');

  // Competition-specific fields
  const [competitionName, setCompetitionName] = useState('');
  const [organization, setOrganization] = useState('');
  const [achievement, setAchievement] = useState('');
  const [compDesc, setCompDesc] = useState('');
  const [compUrl, setCompUrl] = useState('');

  // Certificate-specific fields
  const [certificateName, setCertificateName] = useState('');
  const [issuedBy, setIssuedBy] = useState('');
  const [certificateUrl, setCertificateUrl] = useState('');
  const [certDesc, setCertDesc] = useState('');

  // Internship-specific fields
  const [companyName, setCompanyName] = useState('');
  const [role, setRole] = useState('');
  const [duration, setDuration] = useState('');
  const [internDesc, setInternDesc] = useState('');
  const [internUrl, setInternUrl] = useState('');

  // Shared fields
  const [skills, setSkills] = useState<string[]>(['Python', 'Machine Learning']);
  const [fileName, setFileName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  // Available canonical skills from backend
  const [availableSkills, setAvailableSkills] = useState<ApiSkill[]>([]);

  useEffect(() => {
    skillsApi.getSkills()
      .then((data) => setAvailableSkills(data))
      .catch(() => {
        // Fallback default
      });
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFileName(e.target.files[0].name);
    }
  };

  const handleCategoryChange = (newCategory: SimplifiedCategory) => {
    setCategory(newCategory);
    setErrors({});
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: { [key: string]: string } = {};

    // Validate based on active category
    if (category === 'Project') {
      if (!projectName.trim()) newErrors.projectName = 'Project Name is required';
    } else if (category === 'Competition') {
      if (!competitionName.trim()) newErrors.competitionName = 'Competition / Hackathon Name is required';
      if (!organization.trim()) newErrors.organization = 'Organization / Platform is required';
    } else if (category === 'Certificate') {
      if (!certificateName.trim()) newErrors.certificateName = 'Certificate Name is required';
      if (!issuedBy.trim()) newErrors.issuedBy = 'Issued By is required (e.g. AWS, Coursera, Google)';
    } else if (category === 'Internship') {
      if (!companyName.trim()) newErrors.companyName = 'Company / Organization Name is required';
      if (!role.trim()) newErrors.role = 'Role / Position is required';
    }

    if (skills.length === 0) {
      newErrors.skills = 'Please select at least one skill demonstrated';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    // Prepare unified mapping for backend and passport
    let title = '';
    let issuer = '';
    let description = '';
    let evidenceUrl = '';
    let backendEvidenceType = 'project';
    let displayType = 'Project';

    if (category === 'Project') {
      title = projectName.trim();
      issuer = projectLink.trim() ? 'Independent Project' : 'Self-Directed';
      description = projectDesc.trim() || `Project demonstrating competencies in ${skills.join(', ')}.`;
      evidenceUrl = projectLink.trim();
      backendEvidenceType = 'project';
      displayType = 'Project';
    } else if (category === 'Competition') {
      title = competitionName.trim();
      issuer = organization.trim();
      const compDetails: string[] = [];
      if (achievement.trim()) compDetails.push(`Achievement: ${achievement.trim()}`);
      if (compDesc.trim()) compDetails.push(compDesc.trim());
      description = compDetails.join('\n\n') || `Competition participation demonstrating competencies in ${skills.join(', ')}.`;
      evidenceUrl = compUrl.trim();
      backendEvidenceType = 'competition';
      displayType = 'Competition';
    } else if (category === 'Certificate') {
      title = certificateName.trim();
      issuer = issuedBy.trim();
      description = certDesc.trim() || `Verified certificate issued by ${issuedBy.trim()} demonstrating ${skills.join(', ')}.`;
      evidenceUrl = certificateUrl.trim();
      backendEvidenceType = 'certificate';
      displayType = 'Certificate';
    } else if (category === 'Internship') {
      title = `${role.trim()} at ${companyName.trim()}`;
      issuer = companyName.trim();
      const internDetails: string[] = [];
      if (duration.trim()) internDetails.push(`Duration: ${duration.trim()}`);
      if (internDesc.trim()) internDetails.push(internDesc.trim());
      description = internDetails.join('\n\n') || `Internship experience at ${companyName.trim()} in ${role.trim()}.`;
      evidenceUrl = internUrl.trim();
      backendEvidenceType = 'internship';
      displayType = 'Internship';
    }

    // Map skill names to skill IDs where found in available backend skills
    const resolvedSkillIds: number[] = [];
    skills.forEach((sName) => {
      const match = availableSkills.find(
        (sk) => sk.name.toLowerCase() === sName.toLowerCase()
      );
      if (match) {
        resolvedSkillIds.push(match.id);
      }
    });

    try {
      // Call live backend API to persist evidence record
      const createdEvidence = await evidenceApi.createEvidence({
        student_id: studentId,
        skill_id: resolvedSkillIds.length > 0 ? resolvedSkillIds[0] : undefined,
        skill_ids: resolvedSkillIds,
        skill_names: skills,
        evidence_type: backendEvidenceType,
        title: title,
        description: description,
        issuer: issuer,
        verification_status: 'pending',
        evidence_url: evidenceUrl || undefined,
      });

      // Update parent application state with evidence
      onAddEvidence(
        {
          title: createdEvidence.title || title,
          type: displayType,
          institution: createdEvidence.issuer || issuer,
          skills: skills,
          fileName: fileName || (evidenceUrl ? 'External Link / Proof' : `${title.toLowerCase().replace(/[^a-z0-9]/g, '_')}.pdf`),
          url: createdEvidence.evidence_url || evidenceUrl || undefined,
          score: 95,
          aiFeedback: `Submitted for verification. Demonstrates verified capabilities in ${skills.join(', ')}.`,
        },
        createdEvidence.id
      );

      setIsSubmitting(false);
      onNavigate('passport');
    } catch (err: any) {
      setIsSubmitting(false);
      setSubmitError(err.message || 'Failed to submit evidence to the server. Please check your connection.');
    }
  };

  return (
    <div className="bg-[#f7f9fb] min-h-screen text-[#191c1e] pb-16 font-['Inter']">
      {/* Header */}
      <header className="bg-white sticky top-0 z-40 border-b border-slate-200 flex items-center px-4 sm:px-6 h-13 shadow-2xs">
        <button
          onClick={() => onNavigate('passport')}
          className="p-1.5 mr-2.5 hover:bg-slate-100 rounded-lg transition-colors text-slate-700 flex items-center justify-center cursor-pointer"
          aria-label="Go back to Skill Passport"
        >
          <span className="material-symbols-outlined text-[20px]">arrow_back</span>
        </button>
        <h1 className="font-['Hanken_Grotesk'] text-lg sm:text-xl font-bold text-[#191c1e]">
          Add Evidence
        </h1>
      </header>

      <main className="max-w-[720px] mx-auto w-full px-4 py-4 sm:py-6 flex flex-col gap-4">
        {submitError && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs font-semibold flex items-center gap-2">
            <span className="material-symbols-outlined text-base">error</span>
            <span>{submitError}</span>
          </div>
        )}

        {/* Form Container */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-2xs">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {/* 1. Category Selection */}
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider" htmlFor="evidence-category">
                Evidence Category
              </label>
              <div className="relative">
                <select
                  id="evidence-category"
                  value={category}
                  onChange={(e) => handleCategoryChange(e.target.value as SimplifiedCategory)}
                  className="w-full h-12 bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 appearance-none px-4 pr-10 transition-all outline-none font-medium cursor-pointer"
                >
                  <option value="Project">Project</option>
                  <option value="Competition">Competition</option>
                  <option value="Certificate">Certificate</option>
                  <option value="Internship">Internship / Industry Experience</option>
                </select>
                <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none text-[20px]">
                  expand_more
                </span>
              </div>
            </div>

            {/* 2. Dynamic Fields: PROJECT */}
            {category === 'Project' && (
              <>
                {/* Project Name */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="project-name">
                    Project Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="project-name"
                    type="text"
                    value={projectName}
                    onChange={(e) => {
                      setProjectName(e.target.value);
                      if (errors.projectName) setErrors({ ...errors, projectName: '' });
                    }}
                    placeholder="e.g. Real-Time Collaborative Code Editor"
                    className={`w-full h-12 bg-white border ${
                      errors.projectName ? 'border-red-500' : 'border-slate-200'
                    } text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none`}
                  />
                  {errors.projectName && <span className="text-xs text-red-600 font-medium">{errors.projectName}</span>}
                </div>

                {/* Project Link */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="project-link">
                    Project Link (GitHub / Live Demo)
                  </label>
                  <input
                    id="project-link"
                    type="url"
                    value={projectLink}
                    onChange={(e) => setProjectLink(e.target.value)}
                    placeholder="e.g. https://github.com/username/project or live demo URL"
                    className="w-full h-12 bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
                  />
                </div>

                {/* Project Description */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="project-desc">
                    Project Description / Technical Details <span className="text-slate-400 font-normal lowercase">(optional)</span>
                  </label>
                  <textarea
                    id="project-desc"
                    rows={3}
                    value={projectDesc}
                    onChange={(e) => setProjectDesc(e.target.value)}
                    placeholder="Describe key features, architectural choices, and technologies used..."
                    className="w-full bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg p-3 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
                  />
                </div>
              </>
            )}

            {/* 3. Dynamic Fields: COMPETITION */}
            {category === 'Competition' && (
              <>
                {/* Competition / Hackathon Name */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="comp-name">
                    Competition / Hackathon Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="comp-name"
                    type="text"
                    value={competitionName}
                    onChange={(e) => {
                      setCompetitionName(e.target.value);
                      if (errors.competitionName) setErrors({ ...errors, competitionName: '' });
                    }}
                    placeholder="e.g. Smart India Hackathon 2025, Kaggle Titanic ML"
                    className={`w-full h-12 bg-white border ${
                      errors.competitionName ? 'border-red-500' : 'border-slate-200'
                    } text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none`}
                  />
                  {errors.competitionName && <span className="text-xs text-red-600 font-medium">{errors.competitionName}</span>}
                </div>

                {/* Organization / Platform */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="comp-org">
                    Organization / Platform <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="comp-org"
                    type="text"
                    value={organization}
                    onChange={(e) => {
                      setOrganization(e.target.value);
                      if (errors.organization) setErrors({ ...errors, organization: '' });
                    }}
                    placeholder="e.g. Devpost, Kaggle, ACM, IIT Bombay"
                    className={`w-full h-12 bg-white border ${
                      errors.organization ? 'border-red-500' : 'border-slate-200'
                    } text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none`}
                  />
                  {errors.organization && <span className="text-xs text-red-600 font-medium">{errors.organization}</span>}
                </div>

                {/* Result / Achievement */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="comp-result">
                    Result / Achievement <span className="text-slate-400 font-normal lowercase">(optional)</span>
                  </label>
                  <input
                    id="comp-result"
                    type="text"
                    value={achievement}
                    onChange={(e) => setAchievement(e.target.value)}
                    placeholder="e.g. Winner / 1st Place, Top 10 Finalist, Participant"
                    className="w-full h-12 bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
                  />
                </div>

                {/* Description / Details */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="comp-desc">
                    Description / Details <span className="text-slate-400 font-normal lowercase">(optional)</span>
                  </label>
                  <textarea
                    id="comp-desc"
                    rows={3}
                    value={compDesc}
                    onChange={(e) => setCompDesc(e.target.value)}
                    placeholder="Briefly describe the challenge statement, team solution, or approach..."
                    className="w-full bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg p-3 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
                  />
                </div>

                {/* Proof / Submission Link */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="comp-url">
                    Submission / Leaderboard Link <span className="text-slate-400 font-normal lowercase">(optional)</span>
                  </label>
                  <input
                    id="comp-url"
                    type="url"
                    value={compUrl}
                    onChange={(e) => setCompUrl(e.target.value)}
                    placeholder="e.g. https://devpost.com/software/my-project or leaderboard URL"
                    className="w-full h-12 bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
                  />
                </div>
              </>
            )}

            {/* 4. Dynamic Fields: CERTIFICATE */}
            {category === 'Certificate' && (
              <>
                {/* Certificate Name */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="cert-name">
                    Certificate Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="cert-name"
                    type="text"
                    value={certificateName}
                    onChange={(e) => {
                      setCertificateName(e.target.value);
                      if (errors.certificateName) setErrors({ ...errors, certificateName: '' });
                    }}
                    placeholder="e.g. AWS Certified Solutions Architect, Deep Learning Specialization"
                    className={`w-full h-12 bg-white border ${
                      errors.certificateName ? 'border-red-500' : 'border-slate-200'
                    } text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none`}
                  />
                  {errors.certificateName && <span className="text-xs text-red-600 font-medium">{errors.certificateName}</span>}
                </div>

                {/* Issued By */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="cert-issuer">
                    Issued By <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="cert-issuer"
                    type="text"
                    value={issuedBy}
                    onChange={(e) => {
                      setIssuedBy(e.target.value);
                      if (errors.issuedBy) setErrors({ ...errors, issuedBy: '' });
                    }}
                    placeholder="e.g. Amazon Web Services (AWS), Google Cloud, Coursera, IBM"
                    className={`w-full h-12 bg-white border ${
                      errors.issuedBy ? 'border-red-500' : 'border-slate-200'
                    } text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none`}
                  />
                  {errors.issuedBy && <span className="text-xs text-red-600 font-medium">{errors.issuedBy}</span>}
                </div>

                {/* Certificate Link / Verification Link */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="cert-url">
                    Certificate Link / Verification Link <span className="text-slate-400 font-normal lowercase">(if available)</span>
                  </label>
                  <input
                    id="cert-url"
                    type="url"
                    value={certificateUrl}
                    onChange={(e) => setCertificateUrl(e.target.value)}
                    placeholder="e.g. https://coursera.org/verify/... or Credly badge link"
                    className="w-full h-12 bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
                  />
                </div>

                {/* Certificate Description */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="cert-desc">
                    Description <span className="text-slate-400 font-normal lowercase">(optional)</span>
                  </label>
                  <textarea
                    id="cert-desc"
                    rows={3}
                    value={certDesc}
                    onChange={(e) => setCertDesc(e.target.value)}
                    placeholder="Describe topics mastered, coursework completed, or specializations..."
                    className="w-full bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg p-3 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
                  />
                </div>
              </>
            )}

            {/* 5. Dynamic Fields: INTERNSHIP / INDUSTRY EXPERIENCE */}
            {category === 'Internship' && (
              <>
                {/* Company / Organization Name */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="intern-company">
                    Company / Organization Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="intern-company"
                    type="text"
                    value={companyName}
                    onChange={(e) => {
                      setCompanyName(e.target.value);
                      if (errors.companyName) setErrors({ ...errors, companyName: '' });
                    }}
                    placeholder="e.g. Microsoft, Razorpay, Tech Startup"
                    className={`w-full h-12 bg-white border ${
                      errors.companyName ? 'border-red-500' : 'border-slate-200'
                    } text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none`}
                  />
                  {errors.companyName && <span className="text-xs text-red-600 font-medium">{errors.companyName}</span>}
                </div>

                {/* Role / Position */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="intern-role">
                    Role / Position <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="intern-role"
                    type="text"
                    value={role}
                    onChange={(e) => {
                      setRole(e.target.value);
                      if (errors.role) setErrors({ ...errors, role: '' });
                    }}
                    placeholder="e.g. Full Stack Developer Intern, Data Science Intern"
                    className={`w-full h-12 bg-white border ${
                      errors.role ? 'border-red-500' : 'border-slate-200'
                    } text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none`}
                  />
                  {errors.role && <span className="text-xs text-red-600 font-medium">{errors.role}</span>}
                </div>

                {/* Duration */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="intern-duration">
                    Duration <span className="text-slate-400 font-normal lowercase">(optional)</span>
                  </label>
                  <input
                    id="intern-duration"
                    type="text"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    placeholder="e.g. 3 Months (June 2024 - Aug 2024)"
                    className="w-full h-12 bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
                  />
                </div>

                {/* Description / Work Performed */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="intern-desc">
                    Description / Work Performed <span className="text-slate-400 font-normal lowercase">(optional)</span>
                  </label>
                  <textarea
                    id="intern-desc"
                    rows={3}
                    value={internDesc}
                    onChange={(e) => setInternDesc(e.target.value)}
                    placeholder="Describe key responsibilities, features delivered, and technical tools used..."
                    className="w-full bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg p-3 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
                  />
                </div>

                {/* Verification / Reference Link */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="intern-link">
                    Company / Reference Link <span className="text-slate-400 font-normal lowercase">(optional)</span>
                  </label>
                  <input
                    id="intern-link"
                    type="url"
                    value={internUrl}
                    onChange={(e) => setInternUrl(e.target.value)}
                    placeholder="e.g. https://company.com or recommendation / letter URL"
                    className="w-full h-12 bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
                  />
                </div>
              </>
            )}

            {/* 6. Normalized Searchable Multi-Select Skill Dropdown */}
            <SearchableSkillSelect
              selectedSkills={skills}
              onChange={(updatedSkills) => {
                setSkills(updatedSkills);
                if (errors.skills && updatedSkills.length > 0) {
                  setErrors({ ...errors, skills: '' });
                }
              }}
              error={errors.skills}
              label="Skills Demonstrated (Multiple Selection)"
              placeholder="Type or search skills (e.g. Python, Java, Machine Learning, React)..."
            />

            {/* 7. File Upload Dropzone */}
            <div className="flex flex-col gap-1.5 mt-2">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                {category === 'Project' && 'Upload Project File or Architecture Diagram (Optional)'}
                {category === 'Competition' && 'Upload Certificate or Proof of Rank (Optional)'}
                {category === 'Certificate' && 'Upload Certificate Document (PDF / Image)'}
                {category === 'Internship' && 'Upload Experience Letter or Certificate (Optional)'}
              </label>

              <label 
                htmlFor="file-upload"
                className="w-full border-2 border-dashed border-slate-300 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors flex flex-col items-center justify-center py-6 cursor-pointer group"
              >
                <div className="bg-white p-3 rounded-full mb-2 shadow-2xs group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-[#00687a] text-[26px]">upload_file</span>
                </div>
                <p className="text-xs font-bold text-slate-800 mb-0.5">
                  {fileName ? `Selected: ${fileName}` : 'Click to select document or proof file'}
                </p>
                <p className="text-[11px] text-slate-500">
                  PDF, JPG, PNG or ZIP file (Max 10MB)
                </p>
                <input
                  id="file-upload"
                  type="file"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>

            {/* AI Verification Notice */}
            <div className="mt-2 bg-[#e9ddff] border border-[#d0bcff] rounded-xl p-4 flex gap-3.5 items-start">
              <span className="material-symbols-outlined text-[#6d3bd7] text-[22px] material-symbols-fill shrink-0 mt-0.5">
                auto_awesome
              </span>
              <p className="text-xs text-[#23005c] leading-relaxed">
                <strong className="font-bold text-[#6d3bd7]">Skill Passport Integrity:</strong> All selected skills are normalized and submitted to Neon PostgreSQL. Once verified by an administrator, all skills will automatically be indexed in your Verified Skill Passport and available to Internship & Team Builder matching.
              </p>
            </div>

            {/* Actions */}
            <div className="flex justify-between items-center mt-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => onNavigate('passport')}
                className="text-xs font-semibold text-slate-500 hover:text-slate-800 px-4 py-2 cursor-pointer transition-colors"
              >
                Cancel
              </button>

              <button
                type="submit"
                disabled={isSubmitting}
                className="bg-[#00687a] text-white font-bold text-xs rounded-full px-6 py-3 hover:bg-[#004e5c] transition-all shadow-sm active:scale-95 duration-150 flex items-center gap-2 disabled:opacity-70 cursor-pointer"
              >
                <span>{isSubmitting ? 'Submitting to Backend...' : 'Submit to Skill Passport'}</span>
                <span className="material-symbols-outlined text-[16px]">send</span>
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

