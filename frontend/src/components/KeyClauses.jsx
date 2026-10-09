import React from 'react';
import { Layers, ArrowRight, ShieldCheck } from 'lucide-react';

export default function KeyClauses({ keyClauses = [], onInspectQuote }) {
  if (!keyClauses || keyClauses.length === 0) return null;

  return (
    <div className="mb-10">
      <div className="flex items-center gap-2 mb-1">
        <Layers className="w-5 h-5 text-indigo-400" />
        <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">
          Key Clauses & Commercial Impact
        </h3>
      </div>
      <p className="text-xs text-slate-400 mb-6">
        Structural provisions classified by legal category, practical meaning, and exposure profile.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {keyClauses.map((clause) => {
          const ev = clause.evidence || {};

          return (
            <div
              key={clause.id}
              className="glass-card rounded-xl p-5 border border-slate-800/80 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    {clause.category}
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Page {ev.page || '—'}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white mb-2">{clause.title}</h4>
                <p className="text-xs text-slate-300 leading-relaxed mb-3">
                  {clause.summary}
                </p>

                <div className="rounded-lg bg-slate-950/60 p-2.5 border border-slate-800/60 text-xs text-slate-400 font-mono italic mb-3">
                  "{ev.quote}"
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs">
                <div className="text-slate-300">
                  <span className="font-semibold text-slate-400">Impact: </span>
                  <span className="text-slate-200">{clause.impact}</span>
                </div>

                <button
                  onClick={() => onInspectQuote && onInspectQuote({ page: ev.page, quote: ev.quote })}
                  className="text-sky-400 hover:text-sky-300 ml-3 shrink-0 flex items-center gap-1 font-medium text-[11px]"
                >
                  <span>Locate</span>
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
