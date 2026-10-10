import React, { useState } from 'react';
import { Download, BookOpen, Clock, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

function Facts({ title, items = [], empty, onInspectQuote }) {
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? items : items.slice(0, 3);
  return <section className="rounded-xl border border-slate-700/50 bg-slate-900/40 p-4">
    <h3 className="font-semibold text-white mb-3">{title}</h3>
    {items.length ? <ul className="space-y-4">{visible.map((item, i) => <li key={i}>
      <p className="text-xs text-slate-400 mb-1">{item.label || 'Mentioned in the contract'}</p>
      <div className="flex justify-between items-center gap-3"><strong className="text-teal-300 text-base">{item.value}</strong>
      <button onClick={() => onInspectQuote?.(item.evidence)} className="text-xs text-sky-400">Read page {item.evidence.page}</button></div>
      <details className="text-xs text-slate-400 mt-1"><summary className="cursor-pointer">See the wording</summary><p className="mt-2 leading-relaxed">{item.evidence.quote}</p></details>
    </li>)}</ul> : <p className="text-sm text-slate-400">{empty}</p>}
    {items.length > 3 && <button className="text-xs text-sky-400 mt-4" onClick={() => setExpanded(!expanded)}>{expanded ? 'Show less' : `See all ${items.length} mentions`}</button>}
  </section>;
}

export default function ExecutiveSummaryCard({ analysis, onOpenViewer, onInspectQuote, onOpenSettings, api: propApi }) {
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);
  if (!analysis) return null;
  const summary = analysis.plain_summary;
  const seconds = analysis.analysis_seconds;
  const duration = seconds == null ? 'Time not recorded' : seconds < 1 ? 'Under 1 second' : `${seconds.toFixed(1)} seconds`;
  async function download() {
    setError(''); setDownloading(true);
    try { await (propApi || api).downloadReport(analysis.analysis_id); }
    catch (err) { setError(err.message); }
    finally { setDownloading(false); }
  }
  return <section className="glass-panel rounded-2xl p-5 sm:p-7 mb-8 border border-slate-800">
    <div className="flex flex-wrap justify-between items-start gap-4 mb-5">
      <div><span className="work-eyebrow">YOUR CONTRACT, IN SIMPLE ENGLISH</span><h2 className="text-xl font-bold text-white break-all">{analysis.document_name}</h2></div>
      <div className="work-buttons"><button onClick={onOpenViewer} className="work-secondary"><BookOpen size={15} /> Read contract</button><button onClick={download} disabled={downloading} className="work-primary"><Download size={15} />{downloading ? 'Downloading…' : 'Download report'}</button></div>
    </div>
    {error && <p role="alert" className="work-error">{error}</p>}
    <div className="flex flex-wrap gap-3 text-xs text-slate-400 mb-5">
      <span className="flex items-center gap-1"><Clock size={14} /> Analysis time: {duration}</span>
      <span>{analysis.coverage ? `${analysis.coverage.processed_pages} of ${analysis.coverage.total_pages} pages checked` : 'Page coverage not recorded'}</span>
      <span>{analysis.engine_used?.includes('Heuristic') ? 'Basic automatic review' : 'AI-assisted review'}</span>
    </div>
    <h3 className="font-semibold text-white mb-2">What is this agreement about?</h3>
    <p className="text-sm text-slate-300 leading-relaxed mb-5">{summary?.overview || analysis.document_summary || 'Reopen or re-analyze this contract to get a simple summary.'}</p>
    <div className="work-callout"><strong className="flex items-center gap-2"><CheckCircle2 size={16} /> Result: {summary?.result || `${analysis.risks?.length || 0} items to review.`}</strong><p>This is a list of things to check, not a decision that the contract is safe to sign.</p></div>
    {summary && <>
      <p className="text-xs text-slate-400 mb-3">Actual values from the document. These may include fees, limits or rates; they are not added into a total.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
        <Facts title="Money and rates" items={summary.money} empty="No amounts or rates were found automatically. Check the payment section." onInspectQuote={onInspectQuote} />
        <Facts title="Dates and time periods" items={summary.timing} empty="No dates or time periods were found automatically. Check the term and notice sections." onInspectQuote={onInspectQuote} />
      </div>
      <h3 className="font-semibold text-white mb-2">What should I do next?</h3>
      <ol className="list-decimal pl-5 space-y-2 text-sm text-slate-300">{summary.next_steps.map(step => <li key={step}>{step}</li>)}</ol>
    </>}
    {analysis.llm_notice && <div className="work-callout">{analysis.llm_notice} {onOpenSettings && <button className="underline" onClick={onOpenSettings}>Review AI settings</button>}</div>}
  </section>;
}
