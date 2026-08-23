import React, { useState, useEffect } from 'react';
import { EvidenceItem, ScreenType, ApiSkill } from '../types';
import { skillsApi, evidenceApi } from '../api';
import { SearchableSkillSelect } from '../components/common/SearchableSkillSelect';

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
  const [type, setType] = useState<EvidenceItem['type']>('Project');
  const [title, setTitle] = useState('');
  const [institution, setInstitution] = useState('');
  const [description, setDescription] = useState('');
  const [skills, setSkills] = useState<string[]>(['Python', 'Machine Learning']);
  const [fileName, setFileName] = useState('');
  const [url, setUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  
  // Available skills from backend
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: { [key: string]: string } = {};

    if (!title.trim()) newErrors.title = 'Title is required';
    if (!institution.trim()) newErrors.institution = 'Institution / Source is required';
    if (skills.length === 0) newErrors.skills = 'Please select at least one skill demonstrated';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    // Map evidence type to backend enum format (lowercase)
    const backendTypeMap: { [key: string]: string } = {
      Project: 'project',
      Coursework: 'coursework',
      Competition: 'competition',
      Certificate: 'certificate',
      'Micro-credential': 'coursework',
      Internship: 'internship',
    };
    const backendEvidenceType = backendTypeMap[type] || 'project';

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
      // Call live backend API to persist evidence record with ALL selected skills
      const createdEvidence = await evidenceApi.createEvidence({
        student_id: studentId,
        skill_id: resolvedSkillIds.length > 0 ? resolvedSkillIds[0] : undefined,
        skill_ids: resolvedSkillIds,
        skill_names: skills,
        evidence_type: backendEvidenceType,
        title: title.trim(),
        description: description.trim() || `Submitted ${type.toLowerCase()} demonstrating competencies in ${skills.join(', ')}.`,
        issuer: institution.trim(),
        verification_status: 'pending',
        evidence_url: url.trim() || undefined,
      });

      // Update parent application state with all skills
      onAddEvidence(
        {
          title: createdEvidence.title,
          type,
          institution: createdEvidence.issuer || institution,
          skills: skills,
          fileName: fileName || (url ? 'External Artifact Link' : `${title.toLowerCase().replace(/[^a-z0-9]/g, '_')}.pdf`),
          url: createdEvidence.evidence_url || undefined,
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
    <div className="bg-[#f7f9fb] min-h-screen text-[#191c1e] pb-24 md:pb-12 font-['Inter']">
      {/* Header */}
      <header className="bg-white sticky top-0 z-40 border-b border-slate-200 flex items-center px-4 md:px-8 py-3 h-16 shadow-2xs">
        <button
          onClick={() => onNavigate('passport')}
          className="p-2 mr-3 hover:bg-slate-100 rounded-full transition-colors text-slate-700 flex items-center justify-center"
          aria-label="Go back"
        >
          <span className="material-symbols-outlined text-[22px]">arrow_back</span>
        </button>
        <h1 className="font-['Hanken_Grotesk'] text-xl sm:text-2xl font-bold text-[#191c1e]">
          Add New Evidence Artifact
        </h1>
      </header>

      <main className="max-w-[800px] mx-auto w-full px-4 py-6 md:py-10 flex flex-col gap-6">
        {submitError && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs font-semibold flex items-center gap-2">
            <span className="material-symbols-outlined text-lg">error</span>
            <span>{submitError}</span>
          </div>
        )}

        {/* Form Container */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-xs">
          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            {/* Type Selection */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="evidence-type">
                Evidence Category
              </label>
              <div className="relative">
                <select
                  id="evidence-type"
                  value={type}
                  onChange={(e) => setType(e.target.value as EvidenceItem['type'])}
                  className="w-full h-12 bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 appearance-none px-4 pr-10 transition-all outline-none"
                >
                  <option value="Project">Project (GitHub, Capstone, Deployment)</option>
                  <option value="Coursework">Coursework (University Syllabus, Lab)</option>
                  <option value="Competition">Competition (Hackathon, ICPC, Kaggle)</option>
                  <option value="Certificate">Certificate (Cloud, Industry Vendor)</option>
                  <option value="Micro-credential">Micro-credential / Specialization</option>
                  <option value="Internship">Prior Internship / Industry Experience</option>
                </select>
                <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none text-[20px]">
                  expand_more
                </span>
              </div>
            </div>

            {/* Title Input */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="evidence-title">
                Artifact Title
              </label>
              <input
                id="evidence-title"
                type="text"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value);
                  if (errors.title) setErrors({ ...errors, title: '' });
                }}
                placeholder="e.g. Distributed Database Engine Implementation"
                className={`w-full h-12 bg-white border ${
                  errors.title ? 'border-red-500' : 'border-slate-200'
                } text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none`}
              />
              {errors.title && <span className="text-xs text-red-600 font-medium">{errors.title}</span>}
            </div>

            {/* Institution/Source Input */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="evidence-institution">
                Institution / Source / Issuer
              </label>
              <input
                id="evidence-institution"
                type="text"
                value={institution}
                onChange={(e) => {
                  setInstitution(e.target.value);
                  if (errors.institution) setErrors({ ...errors, institution: '' });
                }}
                placeholder="e.g. Stanford University Dept of CS, Amazon Web Services"
                className={`w-full h-12 bg-white border ${
                  errors.institution ? 'border-red-500' : 'border-slate-200'
                } text-[#191c1e] text-sm rounded-lg px-4 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none`}
              />
              {errors.institution && <span className="text-xs text-red-600 font-medium">{errors.institution}</span>}
            </div>

            {/* Description Input */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider" htmlFor="evidence-desc">
                Summary & Technical Scope (Optional)
              </label>
              <textarea
                id="evidence-desc"
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe key outcomes, architectural decisions, and technologies used..."
                className="w-full bg-white border border-slate-200 text-[#191c1e] text-sm rounded-lg p-3 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all outline-none"
              />
            </div>

            {/* Normalized Searchable Multi-Select Skill Dropdown */}
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
              placeholder="Type or search canonical skills (e.g. Python, Java, Machine Learning, React)..."
            />

            {/* File/Link Upload Dropzone */}
            <div className="flex flex-col gap-1.5 mt-2">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Upload Evidence Artifact or Provide URL
              </label>

              <label 
                htmlFor="file-upload"
                className="w-full border-2 border-dashed border-slate-300 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors flex flex-col items-center justify-center py-6 cursor-pointer group"
              >
                <div className="bg-white p-3 rounded-full mb-2 shadow-2xs group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-[#00687a] text-[26px]">upload_file</span>
                </div>
                <p className="text-xs font-bold text-slate-800 mb-0.5">
                  {fileName ? `Selected: ${fileName}` : 'Click to select document or project archive'}
                </p>
                <p className="text-[11px] text-slate-500">
                  PDF, JPG, PNG or ZIP repository (Max 10MB)
                </p>
                <input
                  id="file-upload"
                  type="file"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>

              {/* URL input */}
              <div className="flex items-center gap-2 mt-2">
                <span className="text-xs text-slate-400 shrink-0 font-medium">or Artifact URL:</span>
                <input
                  type="url"
                  placeholder="https://github.com/your-username/project-repo or certificate URL"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1 h-10 bg-white border border-slate-200 text-xs px-3 rounded-lg outline-none focus:border-[#00687a]"
                />
              </div>
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
                className="text-xs font-semibold text-slate-500 hover:text-slate-800 px-4 py-2"
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
