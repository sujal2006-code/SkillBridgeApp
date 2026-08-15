import React from 'react';
import { ScreenType } from '../types';

interface LandingViewProps {
  onNavigate: (screen: ScreenType) => void;
}

export const LandingView: React.FC<LandingViewProps> = ({ onNavigate }) => {
  return (
    <div className="flex flex-col min-h-screen pb-20 md:pb-0 bg-[#f7f9fb]">
      {/* Hero Section */}
      <section className="relative w-full overflow-hidden bg-white pt-10 pb-16 md:pt-20 md:pb-24 border-b border-slate-200">
        <div className="max-w-[1280px] mx-auto px-4 md:px-8 relative z-10 grid md:grid-cols-2 gap-10 items-center">
          {/* Hero Left Content */}
          <div className="flex flex-col gap-6 text-center md:text-left">
            <div className="inline-flex items-center gap-2 self-center md:self-start px-3 py-1.5 rounded-full bg-cyan-50 border border-cyan-200 text-[#00687a] text-xs font-semibold tracking-wide">
              <span className="material-symbols-outlined text-[16px] material-symbols-fill">verified</span>
              Next-Gen Skill Verification Platform
            </div>

            <h1 className="font-['Hanken_Grotesk'] text-4xl sm:text-5xl md:text-[48px] font-bold text-[#191c1e] leading-[1.15] tracking-tight">
              Turn your learning into <span className="text-[#00687a]">verified opportunities.</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 max-w-lg mx-auto md:mx-0 leading-relaxed">
              Bridging the gap between education and employment with AI-powered skill verification and your personalized Digital Skill Passport.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 justify-center md:justify-start mt-2">
              <button
                onClick={() => onNavigate('dashboard')}
                className="bg-[#00687a] text-white font-semibold text-sm px-6 py-3.5 rounded-lg hover:brightness-110 transition-all shadow-sm flex items-center justify-center gap-2 group"
              >
                <span>Get Started Free</span>
                <span className="material-symbols-outlined text-[18px] group-hover:translate-x-0.5 transition-transform">
                  arrow_forward
                </span>
              </button>
              <button
                onClick={() => onNavigate('internships')}
                className="text-[#00687a] border border-[#00687a] font-semibold text-sm px-6 py-3.5 rounded-lg hover:bg-slate-50 transition-colors flex items-center justify-center gap-2"
              >
                <span className="material-symbols-outlined text-[18px]">work</span>
                <span>Explore Internships</span>
              </button>
            </div>

            {/* Quick Metrics */}
            <div className="pt-4 border-t border-slate-100 flex items-center justify-center md:justify-start gap-6 text-xs text-slate-500">
              <div>
                <span className="font-bold text-slate-800 text-sm block">1,240+</span>
                <span>Verified Students</span>
              </div>
              <div className="h-6 w-px bg-slate-200"></div>
              <div>
                <span className="font-bold text-slate-800 text-sm block">45+</span>
                <span>Hiring Partners</span>
              </div>
              <div className="h-6 w-px bg-slate-200"></div>
              <div>
                <span className="font-bold text-[#10b981] text-sm block">94%</span>
                <span>Placement Fit</span>
              </div>
            </div>
          </div>

          {/* Hero Right Visual */}
          <div className="relative w-full h-[360px] sm:h-[420px] md:h-[480px] rounded-2xl overflow-hidden shadow-lg border border-slate-200 bg-slate-100 flex items-center justify-center group">
            <img
              src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=900&auto=format&fit=crop&q=80"
              alt="Students collaborating on verified skill projects"
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
            />
            {/* Dark overlay gradient */}
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-slate-900/20 to-transparent p-4 sm:p-6 flex flex-col justify-end">
              {/* Floating Verified Badge Card matching Stitch screenshot */}
              <div className="bg-white/95 backdrop-blur-sm rounded-xl p-4 shadow-xl border border-slate-200 max-w-sm w-full self-center sm:self-start flex items-center gap-3.5 transform group-hover:-translate-y-1 transition-transform">
                <div className="w-11 h-11 rounded-xl bg-cyan-100 text-[#00687a] flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-[24px] material-symbols-fill text-[#00687a]">
                    verified
                  </span>
                </div>
                <div>
                  <div className="flex items-center gap-1.5">
                    <p className="text-xs font-bold text-slate-900 uppercase tracking-wider">Skill Verified</p>
                    <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]"></span>
                  </div>
                  <p className="text-sm font-semibold text-slate-700">Advanced Python Data Analysis</p>
                  <p className="text-[11px] text-slate-500">Automated AST & Unit Validation • 98% Score</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* The Future of Credentialing / Bento Grid Section */}
      <section className="bg-[#f7f9fb] py-16 md:py-20">
        <div className="max-w-[1280px] mx-auto px-4 md:px-8">
          <div className="text-center mb-12">
            <h2 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl md:text-[32px] font-bold text-slate-900 tracking-tight">
              The Future of Credentialing
            </h2>
            <p className="text-sm sm:text-base text-slate-600 mt-2 max-w-xl mx-auto">
              Everything you need to prove your worth, land top internships, and assemble project teams.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Feature 1: AI Verification */}
            <div 
              onClick={() => onNavigate('add-evidence')}
              className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-cyan-300 transition-all cursor-pointer group"
            >
              <div className="w-12 h-12 rounded-xl bg-cyan-50 text-[#00687a] flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-[28px]">smart_toy</span>
              </div>
              <h3 className="font-['Hanken_Grotesk'] text-xl font-bold text-slate-900 mb-2 group-hover:text-[#00687a] transition-colors">
                AI-Powered Verification
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Our proprietary AI analyzes your projects, code, and assignments to validate your skills with objective precision.
              </p>
              <div className="mt-4 flex items-center gap-1 text-xs font-bold text-[#00687a]">
                <span>Try Evidence Upload</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </div>
            </div>

            {/* Feature 2: Digital Skill Passport */}
            <div 
              onClick={() => onNavigate('passport')}
              className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-purple-300 transition-all cursor-pointer group"
            >
              <div className="w-12 h-12 rounded-xl bg-[#e9ddff] text-[#6d3bd7] flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-[28px]">badge</span>
              </div>
              <h3 className="font-['Hanken_Grotesk'] text-xl font-bold text-slate-900 mb-2 group-hover:text-[#6d3bd7] transition-colors">
                Digital Skill Passport
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                A portable, shareable portfolio that acts as your definitive source of truth for all verified competencies and achievements.
              </p>
              <div className="mt-4 flex items-center gap-1 text-xs font-bold text-[#6d3bd7]">
                <span>View Skill Passport</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </div>
            </div>

            {/* Feature 3: Matchmaking */}
            <div 
              onClick={() => onNavigate('internships')}
              className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-cyan-300 transition-all cursor-pointer group"
            >
              <div className="w-12 h-12 rounded-xl bg-cyan-50 text-[#00687a] flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-[28px]">handshake</span>
              </div>
              <h3 className="font-['Hanken_Grotesk'] text-xl font-bold text-slate-900 mb-2 group-hover:text-[#00687a] transition-colors">
                Internship Matching
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Seamlessly connect with top employers searching for exactly your verified skill profile, eliminating resume screening bias.
              </p>
              <div className="mt-4 flex items-center gap-1 text-xs font-bold text-[#00687a]">
                <span>Browse Opportunities</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Quick Launch CTA */}
      <section className="bg-white py-12 border-t border-slate-200">
        <div className="max-w-[1000px] mx-auto px-4 text-center">
          <div className="bg-gradient-to-r from-[#004e5c] to-[#00687a] rounded-2xl p-8 sm:p-12 text-white shadow-xl flex flex-col items-center">
            <span className="px-3 py-1 rounded-full bg-white/20 text-xs font-bold uppercase tracking-wider mb-3">
              Ready to verify your expertise?
            </span>
            <h2 className="font-['Hanken_Grotesk'] text-2xl sm:text-3xl font-bold mb-3">
              Explore your personalized dashboard
            </h2>
            <p className="text-white/80 text-sm sm:text-base max-w-md mb-6">
              Track your skill passport completion, review internship matches, and build interdisciplinary teams.
            </p>
            <div className="flex flex-wrap gap-3 justify-center">
              <button
                onClick={() => onNavigate('dashboard')}
                className="bg-white text-[#00687a] px-6 py-3 rounded-lg font-bold text-sm hover:bg-slate-100 transition-colors shadow-sm"
              >
                Go to Student Dashboard
              </button>
              <button
                onClick={() => onNavigate('team-builder')}
                className="bg-[#00424f] border border-white/30 text-white px-6 py-3 rounded-lg font-bold text-sm hover:bg-[#00343f] transition-colors"
              >
                Try Team Builder
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
