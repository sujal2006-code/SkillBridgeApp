import React, { useState } from 'react';
import { VerificationRequest, ScreenType } from '../types';

interface AdminDashboardProps {
  queue: VerificationRequest[];
  totalStudentsCount?: number;
  activeInternshipsCount?: number;
  isLoading?: boolean;
  onApprove: (id: string, apiId?: number) => void;
  onReject: (id: string, apiId?: number) => void;
  onNavigate: (screen: ScreenType) => void;
  onViewSnippet: (req: VerificationRequest) => void;
  onLogout?: () => void;
}

export const AdminDashboardView: React.FC<AdminDashboardProps> = ({
  queue,
  totalStudentsCount = 1,
  activeInternshipsCount = 3,
  isLoading = false,
  onApprove,
  onReject,
  onNavigate,
  onViewSnippet,
  onLogout,
}) => {
  const [filterStatus, setFilterStatus] = useState<'all' | 'pending' | 'reviewed'>('all');

  const pendingItems = queue.filter(item => item.status === 'pending');
  const pendingCount = pendingItems.length;

  const displayedQueue = queue.filter(item => {
    if (filterStatus === 'all') return true;
    if (filterStatus === 'pending') return item.status === 'pending';
    if (filterStatus === 'reviewed') return item.status !== 'pending';
    return true;
  });

  const handleExport = () => {
    const report = {
      generatedAt: new Date().toISOString(),
      metrics: {
        totalStudents: totalStudentsCount,
        activeInternships: activeInternshipsCount,
        pendingVerifications: pendingCount,
      },
      queueSummary: queue.map(q => ({ name: q.studentName, title: q.title, status: q.status, type: q.type }))
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SkillBridge_Audit_Report_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="max-w-[1280px] mx-auto px-4 md:px-8 py-6 md:py-10 pb-24 md:pb-12 min-h-screen">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-purple-100 text-purple-800 border border-purple-200">
              Admin & Verification Console
            </span>
          </div>
          <h1 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl md:text-[32px] font-bold text-[#191c1e] mt-1">
            Platform Overview
          </h1>
          <p className="text-sm md:text-base text-slate-600 mt-0.5">
            Real-time telemetry, verification audit queue, and matching health.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExport}
            className="bg-[#00687a] text-white text-xs font-semibold px-4 py-2.5 rounded-lg hover:brightness-110 transition-all flex items-center gap-2 shadow-2xs"
          >
            <span className="material-symbols-outlined text-[18px]">download</span>
            <span>Export Audit Report</span>
          </button>
          <button
            onClick={onLogout || (() => onNavigate('dashboard'))}
            className="bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-semibold px-4 py-2.5 rounded-lg transition-colors flex items-center gap-1.5 border border-slate-200"
          >
            <span className="material-symbols-outlined text-[18px]">logout</span>
            <span>Exit Admin</span>
          </button>
        </div>
      </div>

      {/* Stats Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Stat 1: Total Students */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs relative overflow-hidden group hover:shadow-md transition-shadow">
          <div className="absolute top-4 right-4 opacity-15 text-slate-400 pointer-events-none">
            <span className="material-symbols-outlined text-6xl">school</span>
          </div>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
            Registered Students
          </p>
          <p className="font-['Hanken_Grotesk'] text-3xl sm:text-4xl font-bold text-slate-900">
            {totalStudentsCount}
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-[#00687a] text-xs font-semibold">
            <span className="material-symbols-outlined text-[16px]">verified_user</span>
            <span>Connected to database</span>
          </div>
        </div>

        {/* Stat 2: Active Internships */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs relative overflow-hidden group hover:shadow-md transition-shadow">
          <div className="absolute top-4 right-4 opacity-15 text-slate-400 pointer-events-none">
            <span className="material-symbols-outlined text-6xl">business_center</span>
          </div>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
            Active Internships
          </p>
          <p className="font-['Hanken_Grotesk'] text-3xl sm:text-4xl font-bold text-[#565e74]">
            {activeInternshipsCount}
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-slate-500 text-xs font-semibold">
            <span className="material-symbols-outlined text-[16px]">schedule</span>
            <span>Live opportunities</span>
          </div>
        </div>

        {/* Stat 3: Pending Verifications */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs relative overflow-hidden group hover:shadow-md transition-shadow">
          <div className="absolute top-4 right-4 opacity-15 text-red-400 pointer-events-none">
            <span className="material-symbols-outlined text-6xl">fact_check</span>
          </div>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
            Pending Verifications
          </p>
          <p className="font-['Hanken_Grotesk'] text-3xl sm:text-4xl font-bold text-[#ba1a1a]">
            {pendingCount}
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-[#ba1a1a] text-xs font-semibold">
            <span className="material-symbols-outlined text-[16px]">warning</span>
            <span>{pendingCount > 0 ? 'Requires attention' : 'Queue fully cleared!'}</span>
          </div>
        </div>
      </div>

      {/* Complex Layout Section: Queue + Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Verification Queue (Spans 2 cols on desktop) */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden flex flex-col">
          <div className="p-5 md:p-6 border-b border-slate-100 flex flex-wrap justify-between items-center gap-3">
            <div>
              <h2 className="font-['Hanken_Grotesk'] text-lg md:text-xl font-bold text-slate-900">
                Live Evidence Verification Queue
              </h2>
              <span className="text-xs text-slate-500">
                Artifacts submitted by students for Skill Passport credentialing
              </span>
            </div>

            <div className="flex gap-1 bg-slate-100 p-1 rounded-lg text-xs">
              <button
                onClick={() => setFilterStatus('all')}
                className={`px-3 py-1 rounded font-semibold transition-colors ${
                  filterStatus === 'all' ? 'bg-white shadow-2xs text-slate-900' : 'text-slate-600'
                }`}
              >
                All ({queue.length})
              </button>
              <button
                onClick={() => setFilterStatus('pending')}
                className={`px-3 py-1 rounded font-semibold transition-colors ${
                  filterStatus === 'pending' ? 'bg-white shadow-2xs text-slate-900' : 'text-slate-600'
                }`}
              >
                Pending ({pendingCount})
              </button>
              <button
                onClick={() => setFilterStatus('reviewed')}
                className={`px-3 py-1 rounded font-semibold transition-colors ${
                  filterStatus === 'reviewed' ? 'bg-white shadow-2xs text-slate-900' : 'text-slate-600'
                }`}
              >
                Reviewed
              </button>
            </div>
          </div>

          <div className="flex-1 p-0">
            {isLoading ? (
              <div className="p-8 text-center text-xs text-slate-500">
                Loading verification queue...
              </div>
            ) : displayedQueue.length === 0 ? (
              <div className="p-12 text-center text-slate-500 text-xs">
                <span className="material-symbols-outlined text-4xl text-slate-300 block mb-1">done_all</span>
                No items matching this filter.
              </div>
            ) : (
              <ul className="divide-y divide-slate-100">
                {displayedQueue.map((req) => (
                  <li
                    key={req.id}
                    className="p-4 md:p-5 hover:bg-slate-50/80 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3 group"
                  >
                    <div className="flex items-center gap-3.5">
                      <div className="w-10 h-10 rounded-full bg-[#dae2fd] text-[#131b2e] flex items-center justify-center font-bold text-xs shrink-0">
                        {req.studentInitials || 'ST'}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-bold text-slate-900">{req.studentName}</p>
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium capitalize">
                            {req.type}
                          </span>
                          {req.status === 'approved' && (
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold">
                              Verified
                            </span>
                          )}
                          {req.status === 'rejected' && (
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-800 font-bold">
                              Rejected
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-600 font-medium mt-0.5">{req.title}</p>
                        <p className="text-[11px] text-slate-400">{req.submittedTime} • {req.skills.join(', ')}</p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 self-end sm:self-center">
                      <button
                        onClick={() => onViewSnippet(req)}
                        className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600 hover:bg-slate-200 transition-colors"
                        title="Review submission details"
                      >
                        <span className="material-symbols-outlined text-[16px]">visibility</span>
                      </button>

                      {req.status === 'pending' ? (
                        <>
                          <button
                            onClick={() => onApprove(req.id, req.apiId)}
                            className="w-8 h-8 rounded-full bg-[#00687a] text-white flex items-center justify-center hover:brightness-110 transition-all shadow-2xs"
                            title="Approve & Verify"
                          >
                            <span className="material-symbols-outlined text-[16px]">check</span>
                          </button>
                          <button
                            onClick={() => onReject(req.id, req.apiId)}
                            className="w-8 h-8 rounded-full bg-slate-100 text-slate-500 hover:text-[#ba1a1a] hover:bg-red-50 transition-colors"
                            title="Reject / Request changes"
                          >
                            <span className="material-symbols-outlined text-[16px]">close</span>
                          </button>
                        </>
                      ) : (
                        <span className="text-xs text-slate-400 font-medium px-2">Completed</span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Matching Insights Card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs p-6 flex flex-col">
          <h2 className="font-['Hanken_Grotesk'] text-lg md:text-xl font-bold text-slate-900 mb-6">
            Matching Insights
          </h2>

          <div className="space-y-6 flex-1">
            {/* Top Verified Skill */}
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                TOP VERIFIED SKILL
              </p>
              <div className="flex items-end gap-2">
                <p className="font-['Hanken_Grotesk'] text-2xl font-bold text-slate-900">
                  Python & FastAPI
                </p>
                <span className="text-[#00687a] text-xs font-bold mb-1 flex items-center">
                  <span className="material-symbols-outlined text-[14px] mr-0.5">trending_up</span>
                  100% Verified
                </span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full mt-3 overflow-hidden">
                <div className="bg-[#00687a] h-full rounded-full w-[90%]"></div>
              </div>
            </div>

            {/* Highest Demand Role */}
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                IN-DEMAND REQUIREMENTS
              </p>
              <div className="flex items-end gap-2">
                <p className="font-['Hanken_Grotesk'] text-xl font-bold text-slate-900">
                  Backend & AI Engineering
                </p>
              </div>
              <div className="flex flex-wrap gap-1.5 mt-3">
                <span className="bg-slate-100 px-2.5 py-1 rounded text-xs font-medium text-slate-700">
                  Python
                </span>
                <span className="bg-slate-100 px-2.5 py-1 rounded text-xs font-medium text-slate-700">
                  FastAPI
                </span>
                <span className="bg-slate-100 px-2.5 py-1 rounded text-xs font-medium text-slate-700">
                  PostgreSQL
                </span>
              </div>
            </div>

            {/* View Full Analytics Button */}
            <div className="mt-auto pt-6 border-t border-slate-100">
              <button
                onClick={handleExport}
                className="w-full border border-slate-200 text-slate-700 text-xs font-bold py-3 rounded-lg hover:bg-slate-50 transition-colors flex items-center justify-center gap-2 shadow-2xs"
              >
                <span className="material-symbols-outlined text-[16px]">bar_chart</span>
                <span>Download Audit Metrics</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
};
