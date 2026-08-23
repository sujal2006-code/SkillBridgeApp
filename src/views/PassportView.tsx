import React, { useState, useMemo } from 'react';
import { Skill, EvidenceItem, ScreenType } from '../types';
import { CircularProgress } from '../components/common/CircularProgress';

interface PassportViewProps {
  skills: Skill[];
  evidenceList: EvidenceItem[];
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  onNavigate: (screen: ScreenType) => void;
  onOpenEvidence: (evidence: EvidenceItem) => void;
}

export const PassportView: React.FC<PassportViewProps> = ({
  skills,
  evidenceList,
  isLoading = false,
  error = null,
  onRetry,
  onNavigate,
  onOpenEvidence,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('All Categories');
  const [activeTab, setActiveTab] = useState<'skills' | 'evidence'>('skills');

  const filterTabs = ['All Categories', 'Programming', 'Backend Development', 'Frontend Development', 'Databases', 'AI / Data Science', 'DevOps / Infrastructure', 'Computer Science', 'Data Analysis'];

  // Filter skills by search and category
  const filteredSkills = useMemo(() => {
    return skills.filter((skill) => {
      const matchesSearch =
        skill.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        skill.category.toLowerCase().includes(searchTerm.toLowerCase());

      if (!matchesSearch) return false;

      if (selectedFilter === 'All Categories') return true;
      return skill.category.toLowerCase() === selectedFilter.toLowerCase();
    });
  }, [skills, searchTerm, selectedFilter]);

  // Filter evidence
  const filteredEvidence = useMemo(() => {
    return evidenceList.filter((ev) => {
      const matchesSearch =
        ev.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ev.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ev.skills.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchesSearch;
    });
  }, [evidenceList, searchTerm]);

  // Group skills by category
  const groupedCategories = useMemo(() => {
    const categories: { [key: string]: Skill[] } = {};
    filteredSkills.forEach((skill) => {
      const cat = skill.category || 'General';
      if (!categories[cat]) {
        categories[cat] = [];
      }
      categories[cat].push(skill);
    });
    return categories;
  }, [filteredSkills]);

  const handleCardClick = (skill: Skill) => {
    // Find the first matching evidence for this skill
    const matchingEvidence = evidenceList.find((e) =>
      e.skills.some(s => s.toLowerCase() === skill.name.toLowerCase()) ||
      (skill.apiId && e.apiId === skill.apiId) ||
      (skill.evidenceIds && skill.evidenceIds.includes(e.id))
    );

    if (matchingEvidence) {
      onOpenEvidence(matchingEvidence);
    } else {
      onOpenEvidence({
        id: `preview-${skill.id}`,
        title: `${skill.name} Competency Assessment & Evidence Record`,
        type: 'Project',
        institution: 'SkillBridge Verification Protocol',
        skills: [skill.name, `${skill.level} Proficiency`],
        date: new Date().toISOString().slice(0, 10),
        verificationStatus: 'verified',
        score: skill.percentage,
        fileName: `${skill.name.toLowerCase().replace(/[^a-z0-9]/g, '_')}_verified_record.pdf`,
        aiFeedback: `Demonstrated competency in ${skill.name} at ${skill.level} level.`
      });
    }
  };

  if (isLoading) {
    return (
      <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-16 flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <CircularProgress percentage={80} size={56} strokeWidth={4.5} color="#00687a" />
        <p className="text-sm font-semibold text-slate-600">Loading Skill Passport data...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-16 flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-16 h-16 rounded-full bg-red-50 text-red-600 flex items-center justify-center border border-red-200">
          <span className="material-symbols-outlined text-3xl">error</span>
        </div>
        <h2 className="text-xl font-bold text-slate-900">Failed to Load Passport Data</h2>
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

  const verifiedCount = skills.filter(s => s.verifiedByAi).length;
  const verifiedEvidenceCount = evidenceList.filter(e => e.verificationStatus === 'verified').length;
  const pendingEvidenceCount = evidenceList.filter(e => e.verificationStatus === 'pending').length;

  return (
    <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-6 md:py-10 pb-24 md:pb-12 min-h-screen">
      {/* Header */}
      <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider bg-cyan-50 text-[#00687a] border border-cyan-200">
              Verified Digital Passport
            </span>
          </div>
          <h1 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl md:text-[32px] font-bold text-[#191c1e] tracking-tight">
            Your Digital Skill Passport
          </h1>
          <p className="text-sm md:text-base text-slate-600 mt-1 max-w-2xl leading-relaxed">
            Manage and showcase your verified competencies. Every skill is backed by verified coursework, projects, competitions, and credentials.
          </p>
        </div>
        <button
          onClick={() => onNavigate('add-evidence')}
          className="self-start md:self-auto bg-[#00687a] text-white px-5 py-2.5 rounded-lg text-sm font-semibold hover:brightness-110 transition-all shadow-xs flex items-center gap-2"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          <span>Add New Evidence</span>
        </button>
      </header>

      {/* Passport View Mode Toggle (Skills vs Evidence Artifacts) */}
      <div className="flex items-center justify-between border-b border-slate-200 mb-6 pb-2">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('skills')}
            className={`pb-2 text-sm font-bold flex items-center gap-2 border-b-2 transition-all ${
              activeTab === 'skills'
                ? 'border-[#00687a] text-[#00687a]'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">workspace_premium</span>
            <span>Passport Skills ({skills.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('evidence')}
            className={`pb-2 text-sm font-bold flex items-center gap-2 border-b-2 transition-all ${
              activeTab === 'evidence'
                ? 'border-[#00687a] text-[#00687a]'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">folder_open</span>
            <span>Evidence Artifacts ({evidenceList.length})</span>
            {pendingEvidenceCount > 0 && (
              <span className="px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px] font-bold">
                {pendingEvidenceCount} Pending
              </span>
            )}
          </button>
        </div>

        <div className="text-xs text-slate-500 hidden sm:block">
          <strong className="text-slate-800">{verifiedCount}</strong> verified skills · <strong className="text-slate-800">{verifiedEvidenceCount}</strong> verified artifacts
        </div>
      </div>

      {/* Search & Filter Controls */}
      <section className="flex flex-col md:flex-row gap-3 mb-8">
        <div className="relative flex-1 max-w-md">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none text-[20px]">
            search
          </span>
          <input
            type="text"
            placeholder={activeTab === 'skills' ? "Search passport skills..." : "Search evidence artifacts..."}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full h-12 pl-10 pr-4 rounded-lg bg-white border border-slate-200 focus:border-[#00687a] focus:ring-2 focus:ring-[#00687a]/20 transition-all text-sm text-[#191c1e] outline-none shadow-2xs"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <span className="material-symbols-outlined text-[18px]">close</span>
            </button>
          )}
        </div>

        {activeTab === 'skills' && (
          <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0 hide-scrollbar items-center">
            {filterTabs.map((tab) => {
              const isActive = selectedFilter === tab;
              return (
                <button
                  key={tab}
                  onClick={() => setSelectedFilter(tab)}
                  className={`px-4 py-2 h-10 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                    isActive
                      ? 'bg-[#00687a] text-white shadow-xs'
                      : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {tab}
                </button>
              );
            })}
          </div>
        )}
      </section>

      {/* Tab 1: Skills Categories */}
      {activeTab === 'skills' && (
        <div className="space-y-10">
          {skills.length === 0 ? (
            <div className="bg-white rounded-2xl border-2 border-dashed border-slate-300 p-12 text-center max-w-lg mx-auto">
              <div className="w-14 h-14 rounded-2xl bg-cyan-50 text-[#00687a] flex items-center justify-center mx-auto mb-4 border border-cyan-200">
                <span className="material-symbols-outlined text-3xl">verified_user</span>
              </div>
              <h3 className="text-xl font-bold text-slate-900 font-['Hanken_Grotesk']">No verified evidence yet</h3>
              <p className="text-sm text-slate-600 mt-2 leading-relaxed">
                Add coursework, projects, competitions or micro-credentials to build your verified skill passport.
              </p>
              <button
                onClick={() => onNavigate('add-evidence')}
                className="mt-6 px-6 py-3 bg-[#00687a] hover:bg-[#004e5c] text-white text-xs font-bold rounded-full transition-all shadow-xs inline-flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-[18px]">add_circle</span>
                <span>+ Add Evidence</span>
              </button>
            </div>
          ) : Object.keys(groupedCategories).length === 0 ? (
            <div className="bg-white rounded-xl border border-dashed border-slate-300 p-12 text-center">
              <span className="material-symbols-outlined text-slate-400 text-5xl mb-2">search_off</span>
              <h3 className="text-lg font-bold text-slate-800">No matching skills found</h3>
              <p className="text-sm text-slate-500 mt-1">Try clearing your search query or switching category filters.</p>
              <button
                onClick={() => { setSearchTerm(''); setSelectedFilter('All Categories'); }}
                className="mt-4 px-4 py-2 bg-[#00687a] text-white text-xs font-bold rounded-lg"
              >
                Reset Filters
              </button>
            </div>
          ) : (
            Object.keys(groupedCategories).map((categoryName) => {
              const categorySkills = groupedCategories[categoryName];
              return (
                <section key={categoryName}>
                  <h2 className="font-['Hanken_Grotesk'] text-xl sm:text-2xl font-bold text-[#191c1e] mb-4 flex items-center justify-between">
                    <span>{categoryName}</span>
                    <span className="text-xs font-semibold text-slate-500">{categorySkills.length} Verified</span>
                  </h2>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {categorySkills.map((skill) => (
                      <div
                        key={skill.id}
                        onClick={() => handleCardClick(skill)}
                        className="bg-white border border-slate-200 rounded-xl p-5 relative hover:shadow-lg hover:border-slate-300 transition-all duration-200 cursor-pointer group flex flex-col justify-between"
                      >
                        {/* Top right Verified badge */}
                        <div className="absolute top-4 right-4 flex items-center gap-1 bg-[#f2f4f6] py-1 px-2.5 rounded-full border border-slate-200 shadow-2xs">
                          <span className="material-symbols-outlined text-[15px] text-[#10b981] material-symbols-fill">
                            verified
                          </span>
                          <span className="text-[11px] font-medium text-slate-600">Verified</span>
                        </div>

                        {/* Progress Ring & Skill Info */}
                        <div className="flex gap-4 items-center mt-3">
                          <CircularProgress
                            percentage={skill.percentage}
                            size={64}
                            strokeWidth={4.5}
                            color="#00687a"
                            fontSize="text-sm font-bold"
                          />
                          <div>
                            <h3 className="font-['Hanken_Grotesk'] text-lg font-bold text-[#191c1e] group-hover:text-[#00687a] transition-colors">
                              {skill.name}
                            </h3>
                            <span className="inline-block bg-[#1e293b] text-white text-[11px] font-medium px-2 py-0.5 rounded mt-1">
                              {skill.level} Proficiency
                            </span>
                          </div>
                        </div>

                        {/* Bottom Evidence Items Bar */}
                        <div className="mt-5 pt-3 border-t border-slate-100 flex justify-between items-center text-xs text-slate-500">
                          <div className="flex items-center gap-1.5">
                            <span className="material-symbols-outlined text-[18px] text-slate-400">folder_open</span>
                            <span className="font-medium">{skill.evidenceCount} Supporting Evidence</span>
                          </div>
                          <button 
                            className="text-[#00687a] group-hover:translate-x-1 p-1 rounded transition-transform"
                            aria-label={`View evidence for ${skill.name}`}
                          >
                            <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              );
            })
          )}
        </div>
      )}

      {/* Tab 2: Evidence Artifacts List */}
      {activeTab === 'evidence' && (
        <div className="space-y-4">
          {filteredEvidence.length === 0 ? (
            <div className="bg-white rounded-xl border border-dashed border-slate-300 p-12 text-center">
              <span className="material-symbols-outlined text-slate-400 text-5xl mb-2">folder_off</span>
              <h3 className="text-lg font-bold text-slate-800">No evidence artifacts found</h3>
              <p className="text-sm text-slate-500 mt-1">Submit coursework, projects, competitions, or certificates to build your passport.</p>
              <button
                onClick={() => onNavigate('add-evidence')}
                className="mt-4 px-4 py-2 bg-[#00687a] text-white text-xs font-bold rounded-lg"
              >
                + Add Evidence
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredEvidence.map((ev) => {
                const isVerified = ev.verificationStatus === 'verified';
                const isPending = ev.verificationStatus === 'pending';

                return (
                  <div
                    key={ev.id}
                    onClick={() => onOpenEvidence(ev)}
                    className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between gap-3 group"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#e9ddff] text-[#6d3bd7] flex items-center justify-center shrink-0">
                          <span className="material-symbols-outlined text-[22px]">folder_open</span>
                        </div>
                        <div>
                          <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
                            {ev.type}
                          </span>
                          <h3 className="font-['Hanken_Grotesk'] text-base font-bold text-slate-900 group-hover:text-[#00687a] transition-colors leading-tight">
                            {ev.title}
                          </h3>
                          <p className="text-xs text-slate-500 mt-0.5">{ev.institution}</p>
                        </div>
                      </div>

                      {/* Status badge */}
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold shrink-0 ${
                        isVerified
                          ? 'bg-emerald-100 text-emerald-800'
                          : isPending
                          ? 'bg-amber-100 text-amber-900'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {isVerified ? 'Verified' : isPending ? 'Pending' : 'Rejected'}
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-100 items-center justify-between">
                      <div className="flex flex-wrap gap-1">
                        {ev.skills.map((s, idx) => (
                          <span key={idx} className="px-2 py-0.5 rounded bg-slate-50 border border-slate-200 text-[11px] text-slate-700 font-medium">
                            {s}
                          </span>
                        ))}
                      </div>
                      <span className="text-xs text-[#00687a] font-semibold flex items-center gap-0.5">
                        <span>Details</span>
                        <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </main>
  );
};
