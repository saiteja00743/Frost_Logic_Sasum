import React from 'react';
import { Calendar, Clock, AlertCircle, CheckCircle2, ArrowRight } from 'lucide-react';

export default function DeadlinesTimeline({ deadlines = [], onInspectQuote }) {
  if (!deadlines || deadlines.length === 0) return null;

  return (
    <div className="mb-10">
      <div className="flex items-center gap-2 mb-1">
        <Calendar className="w-5 h-5 text-sky-400" />
        <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">
          Dates, Deadlines & Notice Windows
        </h3>
      </div>
      <p className="text-xs text-slate-400 mb-6">
        Explicit contractual dates, termination notice windows, and milestone triggers extracted from the document.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {deadlines.map((dl, idx) => {
          const ev = dl.evidence || {};
          const isVerified = dl.verification_status === 'verified';

          return (
            <div
              key={dl.id || idx}
              className="glass-card rounded-xl p-4 sm:p-5 border border-slate-800/90 relative overflow-hidden flex flex-col justify-between"
            >
              <div>
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="p-2 rounded-lg bg-sky-500/10 text-sky-400 shrink-0">
                      <Clock className="w-4 h-4" />
                    </span>
                    <div className="min-w-0">
                      <h4 className="text-sm font-bold text-white leading-snug break-words">{dl.title}</h4>
                      <span className="text-[11px] text-slate-400">{dl.responsible_party}</span>
                    </div>
                  </div>

                  <span
                    className={`text-xs font-bold px-2.5 py-1 rounded-lg border shrink-0 self-start ${
                      dl.is_explicit_date
                        ? 'bg-sky-500/10 text-sky-300 border-sky-500/30'
                        : 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30'
                    }`}
                  >
                    {dl.date_or_trigger}
                  </span>
                </div>

                <div className="text-xs text-slate-400 font-mono bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 mb-3 break-words">
                  <span className="text-teal-400 font-semibold mr-1">Page {ev.page || '—'}:</span>
                  <span className="italic">"{ev.quote}"</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
                {isVerified ? (
                  <span className="text-emerald-400 flex items-center gap-1 font-medium text-[11px]">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Verified Date</span>
                  </span>
                ) : (
                  <span className="text-amber-400 flex items-center gap-1 font-medium text-[11px]">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>Unverified Date</span>
                  </span>
                )}

                <button
                  onClick={() => onInspectQuote && onInspectQuote({ page: ev.page, quote: ev.quote })}
                  className="text-sky-400 hover:text-sky-300 flex items-center gap-1 font-medium text-[11px]"
                >
                  <span>View Passage</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
