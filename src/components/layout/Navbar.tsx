import React, { useState, useEffect } from 'react';
import { ScreenType, ApiTeamInvitation } from '../../types';
import { teamsApi, activitiesApi } from '../../api';

interface NavbarProps {
  currentScreen: ScreenType;
  onNavigate: (screen: ScreenType) => void;
  pendingCount: number;
  studentName?: string;
  studentId?: number;
  onSwitchStudent?: () => void;
  onLogout?: () => void;
  isAdminAuthenticated?: boolean;
  onInvitationAction?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentScreen,
  onNavigate,
  pendingCount,
  studentName = 'Aarav Sharma',
  studentId,
  onSwitchStudent,
  onLogout,
  isAdminAuthenticated = false,
  onInvitationAction,
}) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [invitations, setInvitations] = useState<ApiTeamInvitation[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isActioningId, setIsActioningId] = useState<number | null>(null);

  const fetchInvitations = async () => {
    if (!studentId) return;
    try {
      const invs = await teamsApi.getPendingInvitations();
      setInvitations(invs);
      setUnreadCount(invs.length);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchInvitations();
    const interval = setInterval(fetchInvitations, 15000);
    return () => clearInterval(interval);
  }, [studentId]);

  const handleAccept = async (invitationId: number) => {
    setIsActioningId(invitationId);
    try {
      await teamsApi.acceptInvitation(invitationId);
      setInvitations((prev) => prev.filter((i) => i.id !== invitationId));
      setUnreadCount((prev) => Math.max(0, prev - 1));
      if (onInvitationAction) onInvitationAction();
    } catch (err: any) {
      alert(err.message || 'Failed to accept invitation.');
    } finally {
      setIsActioningId(null);
    }
  };

  const handleReject = async (invitationId: number) => {
    setIsActioningId(invitationId);
    try {
      await teamsApi.rejectInvitation(invitationId);
      setInvitations((prev) => prev.filter((i) => i.id !== invitationId));
      setUnreadCount((prev) => Math.max(0, prev - 1));
      if (onInvitationAction) onInvitationAction();
    } catch (err: any) {
      alert(err.message || 'Failed to reject invitation.');
    } finally {
      setIsActioningId(null);
    }
  };

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
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors cursor-pointer ${
              currentScreen === 'landing' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            Landing
          </button>
          <button
            onClick={() => onNavigate('dashboard')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors cursor-pointer ${
              currentScreen === 'dashboard' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => onNavigate('passport')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors cursor-pointer ${
              currentScreen === 'passport' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            Passport
          </button>
          <button
            onClick={() => onNavigate('internships')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors cursor-pointer ${
              currentScreen === 'internships' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            Internships
          </button>
          <button
            onClick={() => onNavigate('team-builder')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors cursor-pointer ${
              currentScreen === 'team-builder' 
                ? 'text-[#00687a] bg-[#00687a]/10' 
                : 'text-slate-600 hover:text-[#00687a] hover:bg-slate-50'
            }`}
          >
            Team Builder
          </button>
          <button
            onClick={() => onNavigate('add-evidence')}
            className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1 cursor-pointer ${
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
          {/* Real Notification Bell with Badge */}
          <div className="relative">
            <button
              onClick={() => {
                setShowNotifications(!showNotifications);
                fetchInvitations();
              }}
              className="p-2 rounded-full text-slate-600 hover:bg-slate-100 transition-colors relative cursor-pointer"
              title="Team Invitations & Notifications"
              aria-label="Notifications"
            >
              <span className="material-symbols-outlined text-[22px]">notifications</span>
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-5 h-5 bg-[#ba1a1a] text-white text-[10px] font-bold rounded-full flex items-center justify-center animate-pulse">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-2xl shadow-xl border border-slate-200 py-3 z-50 animate-fadeIn text-xs">
                <div className="px-4 pb-2 border-b border-slate-100 flex items-center justify-between">
                  <span className="font-bold text-slate-900 text-sm">Notifications</span>
                  <span className="text-[11px] font-semibold text-slate-500">
                    {invitations.length} Pending Invites
                  </span>
                </div>

                <div className="max-h-72 overflow-y-auto divide-y divide-slate-100">
                  {invitations.length === 0 ? (
                    <div className="py-8 px-4 text-center text-slate-500">
                      <span className="material-symbols-outlined text-3xl text-slate-300 mb-1">mark_email_read</span>
                      <p className="font-medium">No pending team invitations</p>
                      <p className="text-[11px] text-slate-400 mt-0.5">You're all caught up!</p>
                    </div>
                  ) : (
                    invitations.map((inv) => (
                      <div key={inv.id} className="p-3.5 hover:bg-slate-50 flex flex-col gap-2 transition-colors">
                        <div className="flex items-start gap-2.5">
                          <div className="w-8 h-8 rounded-full bg-cyan-100 text-[#00687a] flex items-center justify-center font-bold text-xs shrink-0">
                            <span className="material-symbols-outlined text-[18px]">groups</span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-bold text-slate-800">
                              Invitation to join <span className="text-[#00687a]">"{inv.team_name}"</span>
                            </p>
                            <p className="text-[11px] text-slate-500 mt-0.5">
                              From: {inv.sender_name || 'Teammate'} • Role: <strong className="text-slate-700">{inv.role}</strong>
                            </p>
                            {inv.contributed_skills && inv.contributed_skills.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-1">
                                {inv.contributed_skills.map((sk, idx) => (
                                  <span key={idx} className="text-[9px] font-bold bg-emerald-50 text-emerald-800 px-1.5 py-0.2 rounded border border-emerald-200">
                                    ✓ {sk}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex gap-2 justify-end pt-1">
                          <button
                            onClick={() => handleReject(inv.id)}
                            disabled={isActioningId === inv.id}
                            className="px-3 py-1 text-[11px] font-bold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
                          >
                            Decline
                          </button>
                          <button
                            onClick={() => handleAccept(inv.id)}
                            disabled={isActioningId === inv.id}
                            className="px-3.5 py-1 text-[11px] font-bold text-white bg-[#00687a] hover:bg-[#004e5c] rounded-lg transition-colors shadow-2xs cursor-pointer flex items-center gap-1"
                          >
                            <span>Accept & Join</span>
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Admin Portal Quick Link */}
          <button
            onClick={() => {
              if (isAdminAuthenticated) {
                onNavigate('admin');
              } else {
                onNavigate('admin-login');
              }
            }}
            className={`text-xs font-semibold px-2.5 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 cursor-pointer ${
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
                    className="w-full text-left px-4 py-2 hover:bg-slate-50 text-slate-700 font-medium flex items-center gap-2 cursor-pointer"
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
                      className="w-full text-left px-4 py-2 hover:bg-slate-50 text-slate-700 font-medium flex items-center gap-2 cursor-pointer"
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
                      className="w-full text-left px-4 py-2 hover:bg-red-50 text-red-600 font-medium flex items-center gap-2 border-t border-slate-100 mt-1 cursor-pointer"
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
