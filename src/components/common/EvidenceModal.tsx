import React from 'react';
import { EvidenceItem } from '../../types';

interface EvidenceModalProps {
  isOpen: boolean;
  evidence: EvidenceItem | null;
  onClose: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ isOpen, evidence, onClose }) => {
  if (!isOpen || !evidence) return null;

  const isVerified = evidence.verificationStatus === 'verified';
  const isPending = evidence.verificationStatus === 'pending';

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
            <div className="w-10 h-10 rounded-lg bg-[#e9ddff] text-[#6d3bd7] flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-[24px]">folder_open</span>
            </div>
            <div>
              <span className="text-xs uppercase font-semibold text-slate-500 tracking-wider">
                {evidence.type}
              </span>
              <h3 className="text-lg font-bold text-[#191c1e] font-['Hanken_Grotesk'] leading-tight">
                {evidence.title}
              </h3>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors shrink-0"
            aria-label="Close evidence modal"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Institution & Date */}
        <div className="flex flex-wrap items-center justify-between text-xs text-slate-600 bg-[#f7f9fb] p-3 rounded-lg border border-slate-100">
          <div>
            <span className="text-slate-400 block font-medium">Institution / Source</span>
            <span className="font-semibold text-slate-800">{evidence.institution || 'Verified Credential Issuer'}</span>
          </div>
          <div className="text-right">
            <span className="text-slate-400 block font-medium">Submitted / Verified</span>
            <span className="font-semibold text-slate-800">{evidence.date || 'Recent'}</span>
          </div>
        </div>

        {/* Verification Status Banner */}
        {isVerified ? (
          <div className="bg-[#f0fdf4] border border-[#bbf7d0] p-3.5 rounded-xl flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-[#10b981] text-white flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-[18px]">verified</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-[#166534]">Status: Verified</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-[#dcfce7] text-[#15803d] font-bold">
                  Credited to Passport
                </span>
              </div>
              <p className="text-xs text-[#166534] mt-1 leading-relaxed">
                {evidence.aiFeedback || 'This artifact has passed verification and actively contributes to matching scores.'}
              </p>
            </div>
          </div>
        ) : isPending ? (
          <div className="bg-amber-50 border border-amber-200 p-3.5 rounded-xl flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-amber-500 text-white flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-[18px]">pending</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-amber-800">Status: Pending Verification</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 font-semibold">
                  In Review
                </span>
              </div>
              <p className="text-xs text-amber-700 mt-1 leading-relaxed">
                This item is pending review. In accordance with platform integrity rules, unverified evidence does not affect verified matching scores until confirmed.
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-red-50 border border-red-200 p-3.5 rounded-xl flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-[18px]">block</span>
            </div>
            <div>
              <span className="text-sm font-bold text-red-800">Status: Rejected / Needs Resubmission</span>
              <p className="text-xs text-red-700 mt-1 leading-relaxed">
                Artifact could not be validated. Please resubmit with updated documentation.
              </p>
            </div>
          </div>
        )}

        {/* Skills Validated */}
        {evidence.skills && evidence.skills.length > 0 && (
          <div>
            <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider block mb-2">
              Skills Demonstrated
            </span>
            <div className="flex flex-wrap gap-2">
              {evidence.skills.map((skill, idx) => (
                <span 
                  key={idx} 
                  className="px-3 py-1 bg-[#f2f4f6] text-[#191c1e] text-xs font-medium rounded-full border border-slate-200 flex items-center gap-1.5"
                >
                  <span className={`w-2 h-2 rounded-full ${isVerified ? 'bg-[#10b981]' : 'bg-slate-400'}`}></span>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Artifact File / Link */}
        {(evidence.fileName || evidence.url) && (
          <div className="p-3 border border-dashed border-slate-200 rounded-lg bg-slate-50/50 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 overflow-hidden">
              <span className="material-symbols-outlined text-slate-500 shrink-0">
                {evidence.url ? 'link' : 'description'}
              </span>
              {evidence.url ? (
                <a 
                  href={evidence.url} 
                  target="_blank" 
                  rel="noreferrer"
                  className="font-semibold text-[#00687a] hover:underline truncate"
                >
                  {evidence.url}
                </a>
              ) : (
                <span className="font-medium text-slate-700 truncate">{evidence.fileName}</span>
              )}
            </div>
            <span className="text-slate-500 text-[11px] shrink-0 font-medium ml-2">
              Artifact Link
            </span>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
