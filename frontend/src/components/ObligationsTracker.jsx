import React, { useState } from 'react';
import { CheckCircle2, Clock, AlertCircle, ArrowRight, UserCheck, ShieldCheck } from 'lucide-react';

export default function ObligationsTracker({ obligations = [], parties = [], onInspectQuote }) {
  const [selectedParty, setSelectedParty] = useState('all');

  const filtered = obligations.filter((ob) => {
    if (selectedParty === 'all') return true;
    return ob.responsible_party === selectedParty;
  });

  return (
    <div className="mb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <UserCheck className="w-5 h-5 text-teal-400" />
            <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">
              Contractual Obligations Tracker
            </h3>
          </div>
          <p className="text-xs text-slate-400">
            Assigned duties, operational covenants, and verified performance triggers.
          </p>
        </div>

        {/* Filter by Party */}
        {parties.length > 0 && (
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800">
            <button
              onClick={() => setSelectedParty('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                selectedParty === 'all'
                  ? 'bg-slate-800 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All Parties ({obligations.length})
            </button>
            {parties.map((p, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedParty(p.name)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition truncate max-w-[150px] ${
                  selectedParty === p.name
                    ? 'bg-teal-500/20 text-teal-300 border border-teal-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title={p.name}
              >
                {p.name.split(' ')[0]}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Obligations Grid / Table */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="p-8 rounded-xl bg-slate-900/50 border border-slate-800 text-center text-slate-400 text-sm">
            No obligations found for this party.
          </div>
        ) : (
          filtered.map((item) => {
            const ev = item.evidence || {};
            const isVerified = item.verification_status === 'verified';
            const isDateNeeded = !item.deadline || item.deadline.toLowerCase().includes('verification');

            return (
              <div
                key={item.id}
                className="glass-card glass-card-hover rounded-xl p-4 sm:p-5 border border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <span className="text-xs font-bold px-2.5 py-0.5 rounded-md bg-sky-500/10 text-sky-400 border border-sky-500/20">
                      {item.responsible_party}
                    </span>
                    {item.is_conditional && (
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                        Conditional
                      </span>
                    )}
                  </div>
                  <h4 className="text-sm font-semibold text-white mb-2 leading-snug">
                    {item.obligation}
                  </h4>
                  <div className="text-xs text-slate-400 font-mono bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
                    <span className="text-teal-400 font-semibold mr-1.5">Page {ev.page || '—'}:</span>
                    <span className="italic">"{ev.quote}"</span>
                  </div>
                </div>

                {/* Deadline & Verification Info (Right side) */}
                <div className="flex md:flex-col items-center md:items-end justify-between gap-3 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-800/80">
                  {/* Deadline Pill */}
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span
                      className={`text-xs font-semibold px-2.5 py-1 rounded-lg border ${
                        isDateNeeded
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                          : 'bg-teal-500/10 text-teal-400 border-teal-500/20'
                      }`}
                    >
                      {item.deadline || 'Needs verification'}
                    </span>
                  </div>

                  {/* Verification Pill */}
                  <div className="flex items-center gap-2">
                    {isVerified ? (
                      <span className="text-[11px] font-medium text-emerald-400 flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Verified</span>
                      </span>
                    ) : (
                      <span className="text-[11px] font-medium text-amber-400 flex items-center gap-1">
                        <AlertCircle className="w-3.5 h-3.5" />
                        <span>Unverified</span>
                      </span>
                    )}

                    <button
                      onClick={() => onInspectQuote && onInspectQuote({ page: ev.page, quote: ev.quote })}
                      className="text-xs text-sky-400 hover:text-sky-300 ml-2"
                      title="Inspect quotation in document text"
                    >
                      <ArrowRight className="w-4 h-4" />
                    </button>
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
