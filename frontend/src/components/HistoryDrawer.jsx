import React, { useState, useEffect } from 'react';
import { X, History, FileText, ArrowRight, RefreshCw, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';

export default function HistoryDrawer({ isOpen, onClose, onSelectAnalysis, api: propApi, isGuest }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const apiInstance = propApi || api;
      const items = await apiInstance.getHistory();
      setHistoryItems(items || []);
    } catch (err) {
      console.error('Failed to load history:', err);
      setHistoryItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen, propApi]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/70 backdrop-blur-sm">
      <div className="w-full sm:max-w-md h-full bg-slate-900 border-l border-slate-800 p-4 sm:p-6 flex flex-col shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-sky-400" />
            <div>
              <h3 className="text-base font-bold text-white">Analysis History</h3>
              <p className="text-[10px] text-slate-400">
                {isGuest ? 'Private to your guest session' : 'Your personal contracts'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={fetchHistory}
              disabled={loading}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition"
              title="Refresh"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3">
          {historyItems.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-xs">
              {loading ? 'Loading analysis history...' : 'No contract analyses recorded yet.'}
            </div>
          ) : (
            historyItems.map((item) => {
              const score = item.risk_score || 0;
              const isHigh = score >= 65;
              const isMed = score >= 40 && score < 65;

              return (
                <div
                  key={item.id}
                  onClick={() => onSelectAnalysis(item.id)}
                  className="glass-card rounded-xl p-4 border border-slate-800 hover:border-teal-500/40 hover:bg-slate-800/60 transition cursor-pointer group"
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h4 className="text-xs font-bold text-white truncate group-hover:text-teal-300">
                      {item.filename}
                    </h4>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded border shrink-0 ${
                        isHigh
                          ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                          : isMed
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      }`}
                    >
                      Risk {score}/100
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>{item.contract_type || 'Agreement'}</span>
                    <span>{item.total_pages || 1} pages</span>
                  </div>

                  <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500">
                    <span>{item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent'}</span>
                    <span className="text-teal-400 font-medium group-hover:translate-x-0.5 transition flex items-center gap-0.5">
                      <span>Load Analysis</span>
                      <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
