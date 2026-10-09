import React from 'react';
import { Shield, Sparkles, History, Settings, FileText, Activity } from 'lucide-react';

export default function Navbar({
  backendStatus,
  onOpenSettings,
  onOpenHistory,
  onReset,
  hasAnalysis,
}) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div
          onClick={onReset}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-500 via-teal-400 to-emerald-400 p-[1px] shadow-lg shadow-teal-500/20 group-hover:shadow-teal-500/40 transition">
            <div className="h-full w-full bg-slate-950 rounded-[11px] flex items-center justify-center">
              <Shield className="w-5 h-5 text-teal-400 group-hover:scale-110 transition-transform" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">ClauseGuard</span>
              <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/20">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">Legal Document & Risk Intelligence</p>
          </div>
        </div>

        {/* Actions & Status */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Health status badge */}
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-900 border border-slate-800 text-slate-300">
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === 'online'
                  ? 'bg-emerald-400 animate-pulse'
                  : backendStatus === 'checking'
                  ? 'bg-amber-400'
                  : 'bg-rose-400'
              }`}
            />
            <span>{backendStatus === 'online' ? 'Backend Ready' : 'Connecting...'}</span>
          </div>

          {hasAnalysis && (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <FileText className="w-3.5 h-3.5 text-teal-400" />
              <span>New Document</span>
            </button>
          )}

          <button
            onClick={onOpenHistory}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            title="Analysis History"
          >
            <History className="w-3.5 h-3.5 text-sky-400" />
            <span className="hidden sm:inline">History</span>
          </button>

          <button
            onClick={onOpenSettings}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            title="LLM & Engine Settings"
          >
            <Settings className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden sm:inline">AI Settings</span>
          </button>
        </div>
      </div>
    </header>
  );
}
