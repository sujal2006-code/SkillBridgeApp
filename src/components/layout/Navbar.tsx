import React, { useState } from 'react';
import { ScreenType } from '../../types';

interface NavbarProps {
  currentScreen: ScreenType;
  onNavigate: (screen: ScreenType) => void;
  pendingCount: number;
  studentName?: string;
  onSwitchStudent?: () => void;
  onLogout?: () => void;
  isAdminAuthenticated?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentScreen,
  onNavigate,
  pendingCount,
  studentName = 'Alex Rivera',
  onSwitchStudent,
  onLogout,
  isAdminAuthenticated = false,
}) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const initials = studentName
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'ST';

  return (
    <header className="bg-white border-b border-[#e0e3e5] sticky top-0 z-40 shadow-xs font-['Inter']">
      <div className="max-w-[1280px] mx-auto px-4 md:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <div 
          onClick={() => onNavigate('dashboard')}
          className="flex items-center gap-2.5 cursor-pointer group"
          id="nav-brand-logo"
        >
          <div className="w-9 h-9 rounded-xl bg-[#00687a] text-white flex items-center justify-center font-bold text-sm shadow-xs group-hover:scale-105 transition-transform">
            <span className="material-symbols-outlined text-[22px] material-symbols-fill">widgets</span>
          </div>
          <span className="font-['Hanken_Grotesk'] text-xl font-bold text-[#00687a] tracking-tight">
            SkillBridge
          </span>
        </div>

        {/* Desktop Navigation Links (Student Portal) */}
        <nav className="hidden lg:flex items-center gap-1">
          <button
            onClick={() => onNavigate('landing')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${
              currentScreen === 'landing' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            Landing
          </button>
          <button
            onClick={() => onNavigate('dashboard')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${
              currentScreen === 'dashboard' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => onNavigate('passport')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${
              currentScreen === 'passport' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            Passport
          </button>
          <button
            onClick={() => onNavigate('internships')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${
              currentScreen === 'internships' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            Internships
          </button>
          <button
            onClick={() => onNavigate('team-builder')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${
              currentScreen === 'team-builder' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            Team Builder
          </button>
          <button
            onClick={() => onNavigate('add-evidence')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1 ${
              currentScreen === 'add-evidence' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">add_circle</span>
            Add Evidence
          </button>
        </nav>

        {/* Right Controls */}
        <div className="flex items-center gap-3">
          {/* Admin Portal Quick Link */}
          <button
            onClick={() => {
              if (isAdminAuthenticated) {
                onNavigate('admin');
              } else {
                onNavigate('admin-login');
              }
            }}
            className={`text-xs font-semibold px-2.5 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 ${
              currentScreen === 'admin' || currentScreen === 'admin-login'
                ? 'bg-purple-100 text-purple-800 border-purple-300 font-bold'
                : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-purple-50 hover:text-purple-700 hover:border-purple-200'
            }`}
            title="Faculty & Admin Verification Portal"
          >
            <span className="material-symbols-outlined text-[16px]">admin_panel_settings</span>
            <span className="hidden sm:inline">Admin Portal</span>
            {pendingCount > 0 && (
              <span className="px-1.5 py-0.2 bg-[#ba1a1a] text-white text-[10px] font-bold rounded-full">
                {pendingCount}
              </span>
            )}
          </button>

          {/* Quick Add Evidence button */}
          {currentScreen !== 'landing' && (
            <button
              onClick={() => onNavigate('add-evidence')}
              className="hidden md:flex bg-[#00687a] text-white px-3.5 py-2 rounded-lg text-xs font-semibold hover:brightness-110 transition-all shadow-xs items-center gap-1.5"
            >
              <span className="material-symbols-outlined text-[16px]">upload</span>
              Add Evidence
            </button>
          )}

          {/* Student Profile Pill / Switcher */}
          <div className="relative">
            <div 
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 px-2.5 py-1.5 rounded-full bg-slate-50 border border-slate-200 hover:bg-slate-100 transition-all cursor-pointer"
              title={`${studentName} (Active Student Profile)`}
              id="user-profile-menu-button"
            >
              <div className="w-7 h-7 rounded-full bg-[#dae2fd] text-[#131b2e] flex items-center justify-center font-bold text-xs">
                {initials}
              </div>
              <span className="text-xs font-bold text-slate-800 hidden sm:inline max-w-[100px] truncate">
                {studentName}
              </span>
              <span className="material-symbols-outlined text-slate-400 text-[16px]">expand_more</span>
            </div>

            {/* User Dropdown */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-fadeIn text-xs">
                <div className="px-4 py-2 border-b border-slate-100">
                  <p className="font-bold text-slate-900 truncate">{studentName}</p>
                  <p className="text-[11px] text-slate-400">Student Skill Passport</p>
                </div>
                <div className="py-1">
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      onNavigate('passport');
                    }}
                    className="w-full text-left px-4 py-2 hover:bg-slate-50 text-slate-700 font-medium flex items-center gap-2"
                  >
                    <span className="material-symbols-outlined text-[16px] text-[#00687a]">badge</span>
                    <span>View My Passport</span>
                  </button>
                  {onSwitchStudent && (
                    <button
                      onClick={() => {
                        setShowUserMenu(false);
                        onSwitchStudent();
                      }}
                      className="w-full text-left px-4 py-2 hover:bg-slate-50 text-slate-700 font-medium flex items-center gap-2"
                    >
                      <span className="material-symbols-outlined text-[16px] text-purple-600">switch_account</span>
                      <span>Switch Account</span>
                    </button>
                  )}
                  {onLogout && (
                    <button
                      id="navbar-logout-button"
                      onClick={() => {
                        setShowUserMenu(false);
                        onLogout();
                      }}
                      className="w-full text-left px-4 py-2 hover:bg-red-50 text-red-600 font-medium flex items-center gap-2 border-t border-slate-100 mt-1"
                    >
                      <span className="material-symbols-outlined text-[16px]">logout</span>
                      <span>Log Out</span>
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};


