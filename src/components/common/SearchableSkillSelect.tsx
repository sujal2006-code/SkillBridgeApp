import React, { useState, useRef, useEffect, useMemo } from 'react';
import { CANONICAL_SKILL_CATALOGUE, CanonicalSkill, getSuggestedSkillsForSelected } from '../../data/skillCatalogue';

interface SearchableSkillSelectProps {
  selectedSkills: string[];
  onChange: (skills: string[]) => void;
  error?: string;
  label?: string;
  placeholder?: string;
  maxSkills?: number;
}

export const SearchableSkillSelect: React.FC<SearchableSkillSelectProps> = ({
  selectedSkills,
  onChange,
  error,
  label = 'Skills Demonstrated',
  placeholder = 'Type to search canonical skills (e.g. Python, Java, Machine Learning, React)...',
  maxSkills = 15,
}) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Normalize selected set for quick lookup
  const selectedSet = useMemo(() => {
    return new Set(selectedSkills.map((s) => s.toLowerCase()));
  }, [selectedSkills]);

  // Filter skills based on query
  const filteredSkills = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) {
      // If query is empty, show top popular skills that are not already selected
      return CANONICAL_SKILL_CATALOGUE.filter(
        (s) => !selectedSet.has(s.name.toLowerCase())
      ).slice(0, 10);
    }

    return CANONICAL_SKILL_CATALOGUE.filter((s) => {
      if (selectedSet.has(s.name.toLowerCase())) return false;
      const nameMatch = s.name.toLowerCase().includes(q);
      const catMatch = s.category.toLowerCase().includes(q);
      const descMatch = s.description.toLowerCase().includes(q);
      return nameMatch || catMatch || descMatch;
    }).slice(0, 12);
  }, [query, selectedSet]);

  // Smart suggestions derived from currently selected skills
  const dynamicSuggestions = useMemo(() => {
    return getSuggestedSkillsForSelected(selectedSkills);
  }, [selectedSkills]);

  // Reset highlighted index when filtered list changes
  useEffect(() => {
    setHighlightedIndex(0);
  }, [filteredSkills]);

  // Handle clicking outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectSkill = (skillName: string) => {
    const trimmed = skillName.trim();
    if (!trimmed || selectedSet.has(trimmed.toLowerCase())) return;
    if (selectedSkills.length >= maxSkills) return;

    onChange([...selectedSkills, trimmed]);
    setQuery('');
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    onChange(selectedSkills.filter((s) => s !== skillToRemove));
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (!isOpen) {
        setIsOpen(true);
      } else {
        setHighlightedIndex((prev) => (prev + 1 < filteredSkills.length ? prev + 1 : 0));
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (!isOpen) {
        setIsOpen(true);
      } else {
        setHighlightedIndex((prev) => (prev - 1 >= 0 ? prev - 1 : filteredSkills.length - 1));
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (isOpen && filteredSkills.length > 0 && highlightedIndex < filteredSkills.length) {
        handleSelectSkill(filteredSkills[highlightedIndex].name);
      } else if (query.trim()) {
        // If user typed custom skill not in list
        handleSelectSkill(query.trim());
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    } else if (e.key === 'Backspace' && !query && selectedSkills.length > 0) {
      // Remove last selected chip on backspace if input is empty
      handleRemoveSkill(selectedSkills[selectedSkills.length - 1]);
    }
  };

  return (
    <div className="flex flex-col gap-2 w-full" ref={containerRef}>
      {label && (
        <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center justify-between">
          <span>{label}</span>
          <span className="text-[11px] font-normal text-slate-500">
            {selectedSkills.length} selected
          </span>
        </label>
      )}

      {/* Main Multi-Select Input Box with Selected Chips */}
      <div
        onClick={() => inputRef.current?.focus()}
        className={`min-h-[52px] w-full p-2 bg-white rounded-xl border transition-all flex flex-wrap items-center gap-1.5 cursor-text ${
          error
            ? 'border-red-400 ring-2 ring-red-100'
            : isOpen
            ? 'border-[#00687a] ring-2 ring-cyan-100'
            : 'border-slate-300 hover:border-slate-400'
        }`}
      >
        {/* Selected Skill Chips */}
        {selectedSkills.map((skill) => (
          <span
            key={skill}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-cyan-50 text-[#004e5c] border border-cyan-200 text-xs font-semibold animate-fadeIn shadow-2xs group"
          >
            <span>{skill}</span>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                handleRemoveSkill(skill);
              }}
              className="w-4 h-4 rounded-full flex items-center justify-center hover:bg-cyan-200 text-cyan-700 hover:text-cyan-900 transition-colors cursor-pointer"
              title={`Remove ${skill}`}
              aria-label={`Remove ${skill}`}
            >
              <span className="material-symbols-outlined text-[14px] leading-none">close</span>
            </button>
          </span>
        ))}

        {/* Input for Typing & Searching */}
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={selectedSkills.length === 0 ? placeholder : 'Add more skills...'}
          className="flex-1 min-w-[160px] border-none outline-hidden bg-transparent text-sm text-slate-800 placeholder:text-slate-400 px-1 py-1"
        />

        {query && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setQuery('');
            }}
            className="text-slate-400 hover:text-slate-600 p-1"
            title="Clear search"
          >
            <span className="material-symbols-outlined text-sm">cancel</span>
          </button>
        )}
      </div>

      {error && <p className="text-xs text-red-600 font-medium">{error}</p>}

      {/* Search Dropdown Menu */}
      {isOpen && (
        <div className="relative w-full z-50">
          <div className="absolute top-1 left-0 right-0 max-h-64 overflow-y-auto bg-white rounded-xl border border-slate-200 shadow-xl py-1 divide-y divide-slate-100 animate-fadeIn">
            {filteredSkills.length > 0 ? (
              filteredSkills.map((skill, index) => {
                const isHighlighted = index === highlightedIndex;
                return (
                  <div
                    key={skill.name}
                    onMouseEnter={() => setHighlightedIndex(index)}
                    onClick={() => handleSelectSkill(skill.name)}
                    className={`px-4 py-2.5 flex items-center justify-between cursor-pointer transition-colors ${
                      isHighlighted ? 'bg-cyan-50/80 text-[#00687a]' : 'hover:bg-slate-50 text-slate-800'
                    }`}
                  >
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold">{skill.name}</span>
                        <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                          {skill.category}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">
                        {skill.description}
                      </p>
                    </div>
                    <span className="material-symbols-outlined text-slate-400 text-base">
                      add_circle
                    </span>
                  </div>
                );
              })
            ) : query.trim() ? (
              <div
                onClick={() => handleSelectSkill(query.trim())}
                className="px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-cyan-50 text-slate-700"
              >
                <div className="flex flex-col">
                  <span className="text-sm font-semibold text-[#00687a]">
                    Add custom skill: "{query.trim()}"
                  </span>
                  <span className="text-xs text-slate-500">Not in canonical catalogue, will be registered.</span>
                </div>
                <span className="material-symbols-outlined text-[#00687a] text-lg">
                  add
                </span>
              </div>
            ) : (
              <div className="px-4 py-4 text-center text-xs text-slate-500">
                All matching canonical skills have been selected.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Contextual Smart Skill Suggestions Bar */}
      {dynamicSuggestions.length > 0 && (
        <div className="mt-1 flex flex-col gap-1.5">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-600">
            <span className="material-symbols-outlined text-[14px] text-[#00687a]">
              auto_awesome
            </span>
            <span>Recommended Related Skills:</span>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {dynamicSuggestions.map((sug) => (
              <button
                key={sug}
                type="button"
                onClick={() => handleSelectSkill(sug)}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 hover:bg-cyan-50 hover:text-[#00687a] hover:border-cyan-300 border border-slate-200 transition-all cursor-pointer"
              >
                <span>+ {sug}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
