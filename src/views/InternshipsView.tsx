import React, { useState, useMemo } from 'react';
import { Internship, ScreenType } from '../types';
import { CircularProgress } from '../components/common/CircularProgress';

interface InternshipsViewProps {
  internships: Internship[];
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  onApply: (internshipId: string) => void;
  onOpenMatchModal: (internship: Internship) => void;
  onNavigate: (screen: ScreenType) => void;
}

export const InternshipsView: React.FC<InternshipsViewProps> = ({
  internships,
  isLoading = false,
  error = null,
  onRetry,
  onApply,
  onOpenMatchModal,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRemote, setFilterRemote] = useState(false);
  const [filterFullTime, setFilterFullTime] = useState(false);
  const [filterHighMatch, setFilterHighMatch] = useState(false);

  const filteredInternships = useMemo(() => {
    return internships.filter((item) => {
      const matchesQuery = 
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.verifiedSkills.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()));

      if (!matchesQuery) return false;
      if (filterRemote && !item.location.toLowerCase().includes('remote') && item.type !== 'Remote') return false;
      if (filterFullTime && item.employmentType !== 'Full-time') return false;
      if (filterHighMatch && item.matchPercentage < 80) return false;

      return true;
    });
  }, [internships, searchTerm, filterRemote, filterFullTime, filterHighMatch]);

  if (isLoading) {
    return (
      <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-16 flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <CircularProgress percentage={85} size={56} strokeWidth={4.5} color="#00687a" />
        <p className="text-sm font-semibold text-slate-600">Calculating explainable internship recommendations...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-16 flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-16 h-16 rounded-full bg-red-50 text-red-600 flex items-center justify-center border border-red-200">
          <span className="material-symbols-outlined text-3xl">error</span>
        </div>
        <h2 className="text-xl font-bold text-slate-900">Failed to Load Recommendations</h2>
        <p className="text-sm text-slate-600 text-center max-w-md">{error}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 px-6 py-2 bg-[#00687a] text-white text-xs font-bold rounded-full hover:bg-[#004e5c] transition-colors"
          >
            Retry
          </button>
        )}
      </main>
    );
  }

  return (
    <main className="max-w-[1240px] mx-auto px-4 sm:px-6 py-6 pb-20 md:pb-10 min-h-screen font-['Inter']">
      {/* Header Area */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-5 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2 mb-0.5">
            <span className="px-2 py-0.2 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-50 text-[#6d3bd7] border border-purple-200">
              Deterministic AI Matching
            </span>
          </div>
          <h1 className="font-['Hanken_Grotesk'] text-xl sm:text-2xl font-bold text-[#191c1e] tracking-tight">
            Matching Opportunities
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
            Evaluated directly from your verified Skill Passport data.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full md:w-72">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none text-[18px]">
            search
          </span>
          <input
            type="text"
            placeholder="Search roles, companies, or skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full h-9 pl-9 pr-4 rounded-lg border border-slate-200 bg-white text-xs text-slate-800 focus:outline-none focus:border-[#00687a] focus:ring-1 focus:ring-[#00687a]/20 transition-all shadow-2xs"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[15px]">close</span>
            </button>
          )}
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex overflow-x-auto hide-scrollbar gap-2 mb-8 pb-1 items-center">
        <button
          onClick={() => {
            setFilterRemote(false);
            setFilterFullTime(false);
            setFilterHighMatch(false);
            setSearchTerm('');
          }}
          className={`whitespace-nowrap px-4 py-2 rounded-full border border-slate-200 text-xs font-semibold flex items-center gap-1.5 transition-colors ${
            !filterRemote && !filterFullTime && !filterHighMatch
              ? 'bg-slate-900 text-white'
              : 'bg-white text-slate-700 hover:bg-slate-50'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">filter_list</span>
          All ({internships.length})
        </button>

        <button
          onClick={() => setFilterRemote(!filterRemote)}
          className={`whitespace-nowrap px-4 py-2 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all ${
            filterRemote
              ? 'bg-[#06b6d4] text-[#00424f] border border-cyan-400'
              : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
          }`}
        >
          Remote
          {filterRemote && <span className="material-symbols-outlined text-[14px]">close</span>}
        </button>

        <button
          onClick={() => setFilterHighMatch(!filterHighMatch)}
          className={`whitespace-nowrap px-4 py-2 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all ${
            filterHighMatch
              ? 'bg-[#dae2fd] text-[#131b2e] border border-[#bec6e0]'
              : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
          }`}
        >
          High Match (&gt;= 80%)
          {filterHighMatch && <span className="material-symbols-outlined text-[14px]">close</span>}
        </button>
      </div>

      {/* Internships List */}
      {filteredInternships.length === 0 ? (
        <div className="bg-white rounded-2xl border border-dashed border-slate-300 p-12 text-center">
          <span className="material-symbols-outlined text-slate-400 text-5xl mb-2">work_off</span>
          <h3 className="text-lg font-bold text-slate-800">No matching internships found</h3>
          <p className="text-sm text-slate-500 mt-1">Try resetting your filter parameters or adding more skills to your passport.</p>
          <button
            onClick={() => { setFilterRemote(false); setFilterFullTime(false); setFilterHighMatch(false); setSearchTerm(''); }}
            className="mt-4 px-4 py-2 bg-[#00687a] text-white text-xs font-bold rounded-lg"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          {filteredInternships.map((internship, index) => {
            const isFeatured = index === 0 && internship.matchPercentage >= 90;
            const colSpan = isFeatured ? 'md:col-span-8' : 'md:col-span-6 lg:col-span-4';

            return (
              <div
                key={internship.id}
                className={`${colSpan} bg-white border border-slate-200 rounded-xl p-4 sm:p-4.5 relative overflow-hidden group hover:shadow-sm hover:border-slate-300 transition-all flex flex-col justify-between`}
              >
                {/* Soft decorative gradient background */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#00687a]/5 to-transparent opacity-40 pointer-events-none"></div>

                <div className="relative z-10">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex gap-3 items-start">
                      <div className="w-10 h-10 rounded-lg bg-white border border-slate-200 flex items-center justify-center p-1 shrink-0 overflow-hidden shadow-2xs">
                        <img
                          src={internship.logo}
                          alt={`${internship.company} logo`}
                          className="w-full h-full object-cover rounded-md"
                        />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          {internship.matchPercentage >= 90 && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-[#dae2fd] text-[#131b2e]">
                              Top Match
                            </span>
                          )}
                          <span className="text-slate-400 text-xs flex items-center gap-1">
                            <span className="material-symbols-outlined text-[14px]">schedule</span>
                            {internship.postedDate || 'Active'}
                          </span>
                        </div>
                        <h3 className="font-['Hanken_Grotesk'] text-lg md:text-xl font-bold text-slate-900 group-hover:text-[#00687a] transition-colors leading-tight">
                          {internship.title}
                        </h3>
                        <p className="text-xs text-slate-500 mt-1">
                          {internship.company} • {internship.location}
                        </p>
                      </div>
                    </div>

                    {/* Circular Match Indicator */}
                    <div 
                      onClick={() => onOpenMatchModal(internship)}
                      className="cursor-pointer hover:scale-105 transition-transform shrink-0 ml-2"
                      title="Click to view explainable match breakdown"
                    >
                      <CircularProgress
                        percentage={internship.matchPercentage}
                        size={isFeatured ? 64 : 52}
                        strokeWidth={4}
                        color={internship.matchPercentage >= 90 ? '#00687a' : '#f59e0b'}
                        fontSize={isFeatured ? 'text-sm font-bold' : 'text-xs font-bold'}
                      />
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 line-clamp-2 mt-2 leading-relaxed">
                    {internship.description}
                  </p>

                  {/* Explainability Callout snippet */}
                  {internship.explanation && (
                    <div className="mt-3 p-2.5 bg-purple-50/70 border border-purple-100 rounded-lg text-[11px] text-[#23005c] flex items-start gap-2">
                      <span className="material-symbols-outlined text-[#6d3bd7] text-[15px] shrink-0 mt-0.5">auto_awesome</span>
                      <p className="leading-snug line-clamp-2">
                        {internship.explanation}
                      </p>
                    </div>
                  )}
                </div>

                {/* Verified Skills Match & Actions */}
                <div className="relative z-10 mt-6 pt-4 border-t border-slate-100 flex flex-col sm:flex-row gap-3 justify-between sm:items-end">
                  <div className="flex-1">
                    <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                      Requirements Alignment
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {internship.verifiedSkills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-medium text-emerald-800 flex items-center gap-1"
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]"></span>
                          {skill}
                        </span>
                      ))}
                      {internship.missingSkills && internship.missingSkills.map((skill, idx) => (
                        <span
                          key={`missing-${idx}`}
                          className="px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-xs font-medium text-amber-900 flex items-center gap-1"
                          title="Missing skill requirement"
                        >
                          <span className="material-symbols-outlined text-[12px] text-amber-600">warning</span>
                          Missing {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => onOpenMatchModal(internship)}
                      className="px-3.5 py-2 rounded-full border border-slate-200 bg-white text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors whitespace-nowrap"
                    >
                      View Match
                    </button>
                    <button
                      onClick={() => onApply(internship.id)}
                      disabled={internship.applied}
                      className={`px-5 py-2 rounded-full text-xs font-bold transition-all whitespace-nowrap shadow-xs ${
                        internship.applied
                          ? 'bg-emerald-600 text-white cursor-default'
                          : 'bg-[#00687a] text-white hover:bg-[#004e5c]'
                      }`}
                    >
                      {internship.applied ? 'Applied ✓' : 'Apply Now'}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </main>
  );
};
