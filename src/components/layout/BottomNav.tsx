import React from 'react';
import { ScreenType } from '../../types';

interface BottomNavProps {
  currentScreen: ScreenType;
  onNavigate: (screen: ScreenType) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ currentScreen, onNavigate }) => {
  const isDashboardActive = currentScreen === 'dashboard' || currentScreen === 'landing';
  const isPassportActive = currentScreen === 'passport' || currentScreen === 'add-evidence';
  const isInternshipsActive = currentScreen === 'internships';
  const isTeamsActive = currentScreen === 'team-builder';
  const isAdminActive = currentScreen === 'admin';

  return (
    <nav className="md:hidden fixed bottom-0 w-full z-50 flex justify-around items-center px-2 py-2 bg-white border-t border-[#e0e3e5] shadow-lg">
      {/* Home / Dashboard */}
      <button
        onClick={() => onNavigate('dashboard')}
        className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg transition-all ${
          isDashboardActive 
            ? 'text-[#00687a] font-bold scale-95' 
            : 'text-slate-500 hover:text-[#00687a]'
        }`}
      >
        <span 
          className="material-symbols-outlined text-[24px]"
          style={{ fontVariationSettings: isDashboardActive ? "'FILL' 1" : "'FILL' 0" }}
        >
          home
        </span>
        <span className="text-[11px] font-medium mt-0.5">Home</span>
      </button>

      {/* Passport */}
      <button
        onClick={() => onNavigate('passport')}
        className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg transition-all ${
          isPassportActive 
            ? 'text-[#00687a] font-bold scale-95' 
            : 'text-slate-500 hover:text-[#00687a]'
        }`}
      >
        <span 
          className="material-symbols-outlined text-[24px]"
          style={{ fontVariationSettings: isPassportActive ? "'FILL' 1" : "'FILL' 0" }}
        >
          verified_user
        </span>
        <span className="text-[11px] font-medium mt-0.5">Passport</span>
      </button>

      {/* Internships */}
      <button
        onClick={() => onNavigate('internships')}
        className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg transition-all ${
          isInternshipsActive 
            ? 'text-[#00687a] font-bold scale-95' 
            : 'text-slate-500 hover:text-[#00687a]'
        }`}
      >
        <span 
          className="material-symbols-outlined text-[24px]"
          style={{ fontVariationSettings: isInternshipsActive ? "'FILL' 1" : "'FILL' 0" }}
        >
          work
        </span>
        <span className="text-[11px] font-medium mt-0.5">Internships</span>
      </button>

      {/* Teams */}
      <button
        onClick={() => onNavigate('team-builder')}
        className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg transition-all ${
          isTeamsActive 
            ? 'text-[#00687a] font-bold scale-95' 
            : 'text-slate-500 hover:text-[#00687a]'
        }`}
      >
        <span 
          className="material-symbols-outlined text-[24px]"
          style={{ fontVariationSettings: isTeamsActive ? "'FILL' 1" : "'FILL' 0" }}
        >
          group
        </span>
        <span className="text-[11px] font-medium mt-0.5">Teams</span>
      </button>

      {/* Admin */}
      <button
        onClick={() => onNavigate('admin')}
        className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg transition-all ${
          isAdminActive 
            ? 'text-[#6d3bd7] font-bold scale-95' 
            : 'text-slate-500 hover:text-[#6d3bd7]'
        }`}
      >
        <span 
          className="material-symbols-outlined text-[24px]"
          style={{ fontVariationSettings: isAdminActive ? "'FILL' 1" : "'FILL' 0" }}
        >
          admin_panel_settings
        </span>
        <span className="text-[11px] font-medium mt-0.5">Admin</span>
      </button>
    </nav>
  );
};
