import React from 'react';
import { Internship, TeamCandidate } from '../../types';

interface MatchModalProps {
  isOpen: boolean;
  item: (Internship | TeamCandidate) | null;
  onClose: () => void;
  onApplyOrInvite?: () => void;
}

export const MatchModal: React.FC<MatchModalProps> = ({
  isOpen,
  item,
  onClose,
  onApplyOrInvite,
}) => {
  if (!isOpen || !item) return null;

  const isInternship = 'company' in item;
  const matchPercentage = item.matchPercentage;
  const internshipItem = isInternship ? (item as Internship) : null;
  const candidateItem = !isInternship ? (item as TeamCandidate) : null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-fadeIn"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 flex flex-col gap-4 relative animate-scaleUp max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-cyan-50 border border-cyan-100 text-[#00687a] flex items-center justify-center font-bold text-lg shrink-0">
              {matchPercentage}%
            </div>
            <div>
              <span className="text-xs uppercase font-bold text-[#00687a] tracking-wider">
                {isInternship ? 'Explainable Match Analysis' : 'Team Compatibility Score'}
              </span>
              <h3 className="text-xl font-bold text-[#191c1e] font-['Hanken_Grotesk'] leading-tight">
                {internshipItem ? internshipItem.title : candidateItem?.name}
              </h3>
              <p className="text-xs text-slate-500">
                {internshipItem 
                  ? `${internshipItem.company} • ${internshipItem.location}` 
                  : `${candidateItem?.role} • ${candidateItem?.level}`}
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors shrink-0"
            aria-label="Close modal"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Explainability / AI Matching Rationale Box */}
        <div className="bg-[#e9ddff]/40 border border-[#b395ff]/40 p-4 rounded-xl flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-[#6d3bd7] text-white flex items-center justify-center shrink-0 mt-0.5">
            <span className="material-symbols-outlined text-[18px]">auto_awesome</span>
          </div>
          <div className="text-xs text-[#23005c] flex-1">
            <span className="font-bold block uppercase tracking-wider text-[11px] mb-1">
              Deterministic Matching Explanation
            </span>
            <p className="leading-relaxed text-slate-800">
              {internshipItem?.explanation ||
                candidateItem?.aiInsight ||
                `Your Skill Passport matches ${matchPercentage}% of the prerequisites.`}
            </p>
          </div>
        </div>

        {/* Matched Skills with Supporting Evidence */}
        {internshipItem?.matchedSkillsDetails && internshipItem.matchedSkillsDetails.length > 0 ? (
          <div>
            <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider block mb-2">
              Verified Satisfied Skills & Evidence
            </span>
            <div className="space-y-2">
              {internshipItem.matchedSkillsDetails.map((ms, idx) => (
                <div 
                  key={idx}
                  className="p-3 bg-emerald-50/60 rounded-xl border border-emerald-200 flex flex-col gap-1.5"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-xs text-emerald-900 flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[15px] text-emerald-700">check_circle</span>
                      {ms.skill_name}
                    </span>
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold">
                      {ms.student_proficiency} Proficiency
                    </span>
                  </div>
                  {ms.supporting_evidence && ms.supporting_evidence.length > 0 && (
                    <div className="text-[11px] text-emerald-800 flex items-center gap-1 pl-5">
                      <span className="material-symbols-outlined text-[13px] text-emerald-600">verified</span>
                      <span>Supported by verified {ms.supporting_evidence.map(e => e.evidence_type).join(' & ')}: &ldquo;{ms.supporting_evidence[0].title}&rdquo;</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : candidateItem?.matchedSkillsDetails && candidateItem.matchedSkillsDetails.length > 0 ? (
          <div>
            <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider block mb-2">
              Candidate's Contributed Verified Skills & Evidence
            </span>
            <div className="space-y-2">
              {candidateItem.matchedSkillsDetails.map((ms, idx) => (
                <div 
                  key={idx}
                  className="p-3 bg-emerald-50/60 rounded-xl border border-emerald-200 flex flex-col gap-1.5"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-xs text-emerald-900 flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[15px] text-emerald-700">check_circle</span>
                      {ms.skill_name}
                    </span>
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold">
                      {ms.student_proficiency} Proficiency
                    </span>
                  </div>
                  {ms.supporting_evidence && ms.supporting_evidence.length > 0 && (
                    <div className="text-[11px] text-emerald-800 flex items-center gap-1 pl-5">
                      <span className="material-symbols-outlined text-[13px] text-emerald-600">verified</span>
                      <span>Supported by verified {ms.supporting_evidence.map(e => e.evidence_type).join(' & ')}: &ldquo;{ms.supporting_evidence[0].title}&rdquo;</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div>
            <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider block mb-2">
              Verified Skill Alignment
            </span>
            <div className="flex flex-wrap gap-2">
              {item.verifiedSkills.map((skill, idx) => (
                <span 
                  key={idx}
                  className="px-3 py-1 bg-emerald-50 text-emerald-800 text-xs font-semibold rounded-full border border-emerald-200 flex items-center gap-1.5"
                >
                  <span className="material-symbols-outlined text-[14px] text-emerald-600">verified</span>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Missing Required Skills / Unfilled Team Skills */}
        {((internshipItem?.missingSkills && internshipItem.missingSkills.length > 0) || (candidateItem?.missingSkills && candidateItem.missingSkills.length > 0)) && (
          <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-xl">
            <span className="text-xs font-bold uppercase text-amber-900 tracking-wider block mb-1.5 flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px] text-amber-600">warning</span>
              {isInternship ? 'Missing Skills (Recommended to Develop Next)' : 'Missing Team Requirements'}
            </span>
            <div className="flex flex-wrap gap-1.5">
              {(internshipItem?.missingSkills || candidateItem?.missingSkills || []).map((skill, idx) => (
                <span 
                  key={idx}
                  className="px-2.5 py-1 bg-white text-amber-900 text-xs font-semibold rounded-md border border-amber-300 flex items-center gap-1"
                >
                  <span className="material-symbols-outlined text-[13px] text-amber-600">close</span>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Complementary Domain Breadth Skills */}
        {candidateItem?.complementarySkills && candidateItem.complementarySkills.length > 0 && (
          <div>
            <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider block mb-2">
              Complementary Domain Breadth Skills
            </span>
            <div className="flex flex-wrap gap-1.5">
              {candidateItem.complementarySkills.map((skill, idx) => (
                <span 
                  key={idx}
                  className="px-2.5 py-1 bg-cyan-50 text-[#004e5c] text-xs font-semibold rounded-md border border-cyan-200 flex items-center gap-1"
                >
                  <span className="material-symbols-outlined text-[13px] text-[#00687a]">extension</span>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end gap-3 pt-3 border-t border-slate-100 mt-1">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-full transition-colors"
          >
            Dismiss
          </button>
          {onApplyOrInvite && (
            <button
              onClick={() => {
                onApplyOrInvite();
                onClose();
              }}
              className="px-6 py-2 text-xs font-bold text-white bg-[#00687a] hover:bg-[#004e5c] rounded-full transition-colors shadow-sm flex items-center gap-2"
            >
              {isInternship ? 'Apply with Skill Passport' : 'Send Team Invitation'}
              <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
