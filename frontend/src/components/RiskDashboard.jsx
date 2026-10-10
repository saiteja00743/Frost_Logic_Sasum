import React, { useState } from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Search, ArrowRight, ShieldAlert, Sparkles, Filter } from 'lucide-react';

export default function RiskDashboard({ risks = [], onInspectQuote }) {
  const [activeFilter, setActiveFilter] = useState('all');

  const highCount = risks.filter((r) => r.severity === 'high').length;
  const medCount = risks.filter((r) => r.severity === 'medium').length;
  const lowCount = risks.filter((r) => r.severity === 'low').length;

  const filteredRisks = risks.filter((r) => {
    if (activeFilter === 'all') return true;
    return r.severity === activeFilter;
  });

  return (
    <div className="mb-10">
      {/* Section Header */}
      <div className="flex flex-col gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">
              Evidence-Linked Risk Analysis
            </h3>
          </div>
          <p className="text-xs text-slate-400">
            Every risk finding is paired with verbatim document evidence, page location, and verification status.
          </p>
        </div>

        {/* Severity Filter Tabs — scrollable on mobile */}
        <div className="overflow-x-auto pb-1 -mx-1 px-1">
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 w-max min-w-full sm:w-auto sm:min-w-0">
            <button
              onClick={() => setActiveFilter('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition whitespace-nowrap ${
                activeFilter === 'all'
                  ? 'bg-slate-800 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All ({risks.length})
            </button>
            <button
              onClick={() => setActiveFilter('high')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 whitespace-nowrap ${
                activeFilter === 'high'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  : 'text-rose-400 hover:text-rose-300'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0" />
              High ({highCount})
            </button>
            <button
              onClick={() => setActiveFilter('medium')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 whitespace-nowrap ${
                activeFilter === 'medium'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'text-amber-400 hover:text-amber-300'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
              Medium ({medCount})
            </button>
            <button
              onClick={() => setActiveFilter('low')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 whitespace-nowrap ${
                activeFilter === 'low'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'text-emerald-400 hover:text-emerald-300'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
              Low ({lowCount})
            </button>
          </div>
        </div>
      </div>

      {/* Risks List */}
      <div className="space-y-4">
        {filteredRisks.length === 0 ? (
          <div className="p-8 rounded-xl bg-slate-900/50 border border-slate-800 text-center text-slate-400 text-sm">
            No risks found for this filter category.
          </div>
        ) : (
          filteredRisks.map((risk) => {
            const isHigh = risk.severity === 'high';
            const isMed = risk.severity === 'medium';
            const isVerified = risk.verification_status === 'verified';
            const ev = risk.evidence || {};

            return (
              <div
                key={risk.id}
                className="glass-card glass-card-hover rounded-2xl p-5 sm:p-6 border border-slate-800/90 relative overflow-hidden"
              >
                {/* Header: Title & Badges */}
                <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span
                        className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded tracking-wider border ${
                          isHigh
                            ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                            : isMed
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                            : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        }`}
                      >
                        {risk.severity} Risk
                      </span>
                      <span className="text-xs text-slate-400 font-medium">
                        {risk.category || 'General'}
                      </span>
                    </div>
                    <h4 className="text-base font-bold text-white tracking-tight">
                      {risk.title}
                    </h4>
                  </div>

                  {/* Verification Status Badge */}
                  <div className="flex items-center gap-2">
                    {isVerified ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Verified (Page {ev.page || '—'})</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        <span>Unverified / Needs Review</span>
                      </span>
                    )}
                  </div>
                </div>

                {/* Explanation */}
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed mb-4">
                  {risk.explanation}
                </p>

                {/* Verbatim Supporting Evidence Box */}
                <div className="rounded-xl bg-slate-950/70 border border-slate-800/90 p-3.5 sm:p-4 mb-4">
                  <div className="flex items-center justify-between text-[11px] text-slate-400 mb-2 font-mono">
                    <span className="font-semibold text-teal-400 flex items-center gap-1">
                      <span>Source Quote</span>
                      <span>(Page {ev.page || 'N/A'})</span>
                    </span>
                    <button
                      onClick={() => onInspectQuote && onInspectQuote({ page: ev.page, quote: ev.quote })}
                      className="text-sky-400 hover:text-sky-300 hover:underline flex items-center gap-1 cursor-pointer"
                    >
                      <span>Locate in Source</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                  <blockquote className="text-xs text-slate-200 italic font-mono leading-relaxed border-l-2 border-teal-500/50 pl-3">
                    "{ev.quote}"
                  </blockquote>
                </div>

                {/* Recommended Action */}
                <div className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 text-xs">
                  <Sparkles className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-slate-200">Recommended Action: </span>
                    <span className="text-slate-300">{risk.recommended_action}</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
