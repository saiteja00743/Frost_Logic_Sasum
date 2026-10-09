import React from 'react';
import { Download, FileText, CheckCircle2, AlertTriangle, Users, BookOpen, ShieldAlert, Cpu } from 'lucide-react';
import { api } from '../services/api';

export default function ExecutiveSummaryCard({ analysis, onOpenViewer }) {
  if (!analysis) return null;

  const riskScore = analysis.risk_score || 0;
  const isHighRisk = riskScore >= 65;
  const isMedRisk = riskScore >= 40 && riskScore < 65;

  const scoreBadgeColor = isHighRisk
    ? 'text-rose-400 bg-rose-500/10 border-rose-500/30'
    : isMedRisk
    ? 'text-amber-400 bg-amber-500/10 border-amber-500/30'
    : 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';

  const verif = analysis.verification_summary || {};
  const verifRate = verif.verification_rate_percent ?? 100;
  const verifiedCount = verif.verified_count ?? 0;
  const totalChecked = verif.total_items_checked ?? 0;

  const handleDownloadReport = () => {
    if (!analysis.analysis_id) return;
    const url = api.getReportDownloadUrl(analysis.analysis_id);
    window.open(url, '_blank');
  };

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 shadow-2xl relative overflow-hidden mb-8">
      {/* Top Banner & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
              {analysis.contract_type || 'Commercial Agreement'}
            </span>
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Cpu className="w-3 h-3 text-sky-400" />
              {analysis.engine_used || 'ClauseGuard AI Engine'}
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            {analysis.document_name || 'Document Analysis'}
          </h2>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onOpenViewer}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            <BookOpen className="w-4 h-4 text-sky-400" />
            <span>View Source Document</span>
          </button>

          <button
            onClick={handleDownloadReport}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-teal-500 to-sky-600 hover:from-teal-400 hover:to-sky-500 text-white shadow-lg shadow-teal-500/20 transition"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF Report</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Score Gauge + Stats + Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-6">
        {/* Risk Score Gauge (3 cols) */}
        <div className="lg:col-span-3 flex flex-col items-center justify-center p-6 rounded-xl bg-slate-900/80 border border-slate-800/90 text-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Contract Risk Level
          </span>
          <div className="relative w-28 h-28 flex items-center justify-center my-2">
            {/* SVG circular meter */}
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-slate-800"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className={isHighRisk ? 'text-rose-500' : isMedRisk ? 'text-amber-500' : 'text-emerald-500'}
                strokeDasharray={`${riskScore}, 100`}
                strokeWidth="3.5"
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
              <span className="text-3xl font-extrabold text-white tracking-tight">{riskScore}</span>
              <span className="text-[10px] text-slate-400 font-medium">/ 100</span>
            </div>
          </div>
          <span className={`text-xs font-bold px-3 py-1 rounded-full border ${scoreBadgeColor}`}>
            {isHighRisk ? 'High Risk Review' : isMedRisk ? 'Moderate Risk' : 'Low / Standard Risk'}
          </span>
        </div>

        {/* Executive Summary & Verification Badge (9 cols) */}
        <div className="lg:col-span-9 flex flex-col justify-between">
          <div>
            {/* Verification Audit Banner */}
            <div className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-medium mb-4">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>
                <strong>Evidence Audit Passed:</strong> {verifRate}% of findings ({verifiedCount} of {totalChecked} quotes) verified against raw document text.
              </span>
            </div>

            <h3 className="text-sm font-semibold text-slate-300 mb-2">Executive Summary</h3>
            <p className="text-sm text-slate-300 leading-relaxed bg-slate-900/40 p-4 rounded-xl border border-slate-800/60 mb-4">
              {analysis.document_summary || 'No summary available.'}
            </p>
          </div>

          {/* Contracting Parties & Meta Pills */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {analysis.parties && analysis.parties.map((party, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800/80"
              >
                <div className="w-8 h-8 rounded-lg bg-sky-500/10 text-sky-400 flex items-center justify-center shrink-0">
                  <Users className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-bold text-white truncate">{party.name}</p>
                  <p className="text-[11px] text-slate-400 truncate">{party.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Metric Counters footer */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-slate-800/80 text-center">
        <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/60">
          <span className="text-lg font-bold text-white">{analysis.total_pages || 1}</span>
          <p className="text-[11px] text-slate-400">Total Pages</p>
        </div>
        <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/60">
          <span className="text-lg font-bold text-white">{analysis.word_count ? analysis.word_count.toLocaleString() : 0}</span>
          <p className="text-[11px] text-slate-400">Word Count</p>
        </div>
        <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/60">
          <span className="text-lg font-bold text-rose-400">{analysis.risks ? analysis.risks.length : 0}</span>
          <p className="text-[11px] text-slate-400">Identified Risks</p>
        </div>
        <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/60">
          <span className="text-lg font-bold text-teal-400">{analysis.obligations ? analysis.obligations.length : 0}</span>
          <p className="text-[11px] text-slate-400">Key Obligations</p>
        </div>
      </div>
    </div>
  );
}
