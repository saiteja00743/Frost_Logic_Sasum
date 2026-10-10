import { useCallback, useEffect, useState } from 'react';
import { ArrowUpRight, Bell, CalendarDays, CheckCircle2, FileText, Plus, Search } from 'lucide-react';
import ActionEditor, { Modal } from './ActionEditor';
import './workspace.css';

function eventText(event) {
  if (!['confirmed', 'updated'].includes(event.kind)) return event.detail;
  try {
    const details = JSON.parse(event.detail);
    const labels = { owner: 'Owner', due_date: 'Deadline', timezone: 'Time zone', renewal_date: 'Renewal date', notice_days: 'Notice days', note: 'Note', notes: 'Notes', title: 'Action' };
    return Object.entries(details).filter(([, value]) => value !== null && value !== '').map(([key, value]) =>
      `${labels[key] || key}: ${value && typeof value === 'object' ? `${value.before ?? 'Not set'} → ${value.after ?? 'Not set'}` : value}`
    ).join('\n') || 'Details reviewed and reconfirmed.';
  } catch { return event.detail; }
}

function daysUntil(action) {
  const parts = new Intl.DateTimeFormat('en-CA', { timeZone: action.timezone, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date());
  const value = type => parts.find(p => p.type === type).value;
  const today = `${value('year')}-${value('month')}-${value('day')}`;
  return Math.round((Date.parse(`${action.due_date}T00:00:00Z`) - Date.parse(`${today}T00:00:00Z`)) / 86400000);
}
function dueLabel(action) {
  if (action.status !== 'open') return action.status;
  const days = daysUntil(action);
  return days < 0 ? `${-days} days overdue` : days === 0 ? 'Due today' : `Due in ${days} days`;
}

export function DeadlineReview({ api, analysis, onInspectQuote }) {
  const [selected, setSelected] = useState(null);
  const [message, setMessage] = useState('');
  return <section className="work-panel work-review">
    <div className="work-section-heading"><div><span className="work-eyebrow">FROM FINDING TO ACTION</span><h2>Confirm deadlines worth tracking</h2></div><CalendarDays size={24} /></div>
    <p className="work-muted">Extracted dates are suggestions. Review the passage, assign an internal owner, and confirm an action deadline.</p>
    {message && <p role="status" className="work-success">{message}</p>}
    {(analysis.deadlines || []).length ? <div className="work-review-list">{analysis.deadlines.map(d => <div key={d.id}>
      <div><strong>{d.title}</strong><p className="work-muted">{d.date_or_trigger} · Page {d.evidence?.page || 'unknown'}</p></div>
      <div className="work-buttons"><button className="work-secondary" onClick={() => onInspectQuote(d.evidence || {})}>View source</button><button className="work-primary" onClick={() => { setSelected(d); setMessage(''); }}>Review & track</button></div>
    </div>)}</div> : <p className="work-callout">No deadlines were extracted. You can still create a manually confirmed action from the workspace.</p>}
    {selected && <ActionEditor api={api} analysis={analysis} deadline={selected}
      contract={{ id: analysis.document_id, filename: analysis.document_name }}
      onClose={() => setSelected(null)} onSaved={() => { setSelected(null); setMessage('Action saved. Open Workspace to track it and view reminders.'); }} />}
  </section>;
}

export default function ContractWorkspace({ api, onUpload, onOpenContract }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [tab, setTab] = useState('actions');
  const [filter, setFilter] = useState('open');
  const [search, setSearch] = useState('');
  const [editor, setEditor] = useState(null);
  const [detail, setDetail] = useState(null);
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState('completed');
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const load = useCallback(async () => {
    try { const result = await api.workspace(); setData(result); setError(''); }
    catch (err) { setError(err.message); }
  }, [api]);
  useEffect(() => { load(); const timer = setInterval(load, 60000); return () => clearInterval(timer); }, [load]);
  const open = data?.actions.filter(a => a.status === 'open') || [];
  const overdue = open.filter(a => daysUntil(a) < 0).length;
  const upcoming = open.filter(a => daysUntil(a) >= 0 && daysUntil(a) <= 30).length;
  const unread = data?.reminders.filter(r => !r.read_at).length || 0;
  const actions = (data?.actions || []).filter(a => (filter === 'all' || a.status === filter) && `${a.title} ${a.owner} ${a.document_name}`.toLowerCase().includes(search.toLowerCase()));
  const contracts = (data?.contracts || []).filter(c => c.filename.toLowerCase().includes(search.toLowerCase()));
  async function inspect(action) {
    setDetail(action); setEvents(null); setNote(''); setStatus(action.status === 'open' ? 'completed' : 'open');
    try { setEvents(await api.workspace(`/actions/${action.id}/events`)); }
    catch (err) { setError(err.message); setDetail(null); }
  }
  async function saveStatus(e) {
    e.preventDefault(); setBusy(true); setError('');
    try {
      await api.workspace(`/actions/${detail.id}/status`, 'PATCH', { status, note, version: detail.version });
      setDetail(null); setNotice('Action updated. Your note is saved in its activity history.'); await load();
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  async function download(action) {
    try { await api.downloadCalendar(action.id); setNotice('Calendar downloaded. Import it into your calendar; reminders depend on your calendar settings. Re-export after changing the deadline.'); }
    catch (err) { setError(err.message); }
  }
  return <div className="work-root">
    <div className="work-hero"><div><span className="work-eyebrow">YOUR CONTRACT WORKSPACE</span><h1>Stay ahead of the next deadline.</h1><p>Give every vendor commitment a date, an owner, and a clear next step.</p></div><button className="work-primary" onClick={onUpload}><Plus size={17} /> Add contract</button></div>
    {data?.demo && <div className="work-demo">Demo workspace · Saved in this browser’s signed session for up to 7 days. Use sample agreements here; sign in for your business contracts.</div>}
    {error && <div className="work-error" role="alert">{error} <button onClick={load}>Retry</button></div>}
    {notice && <div className="work-success" role="status">{notice}<button aria-label="Dismiss message" onClick={() => setNotice('')}> ×</button></div>}
    {!data ? <div className="work-empty">{error ? 'Your workspace could not be loaded.' : 'Loading your workspace…'}</div> : <>
      <div className="work-stats">
        {[[FileText, data.contracts.length, 'Contracts'], [CalendarDays, upcoming, 'Due within 30 days'], [Bell, overdue, 'Overdue actions'], [CheckCircle2, data.actions.filter(a => a.status === 'completed').length, 'Completed']].map(([Icon, value, label]) => <div className="work-stat" key={label}><Icon size={19} /><strong>{value}</strong><span>{label}</span></div>)}
      </div>
      <section className="work-panel">
        <div className="work-toolbar"><div className="work-tabs" role="tablist" aria-label="Workspace view">{[['actions', 'Actions'], ['contracts', 'Contracts'], ['reminders', `Inbox${unread ? ` (${unread})` : ''}`]].map(([id, label]) => <button role="tab" aria-selected={tab === id} key={id} onClick={() => { setTab(id); setSearch(''); }}>{label}</button>)}</div>
          {tab !== 'reminders' && <label className="work-search"><Search size={16} /><input aria-label="Search workspace" placeholder="Search contracts, actions, owners…" value={search} onChange={e => setSearch(e.target.value)} /></label>}
        </div>
        {tab === 'actions' && <>
          <div className="work-section-heading"><p className="work-muted">Confirmed commitments across your contracts</p><select aria-label="Filter action status" value={filter} onChange={e => setFilter(e.target.value)}><option value="open">Open actions</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option><option value="all">All actions</option></select></div>
          {actions.length ? <div className="work-action-list">{actions.map(a => <article className="work-action" key={a.id}>
            <div className="work-action-main"><span className={`work-pill ${a.status === 'open' && daysUntil(a) < 0 ? 'work-danger' : ''}`}>{dueLabel(a)}</span><h3>{a.title}</h3><p className="work-muted">{a.document_name}</p><p className="work-action-meta"><strong>{a.owner}</strong><span>{a.due_date} · {a.timezone}</span></p>{a.notes && <p className="work-note">{a.notes}</p>}</div>
            <div className="work-buttons"><button className="work-secondary" onClick={() => inspect(a)}>Activity & status</button>{a.status === 'open' && <><button className="work-secondary" onClick={() => setEditor({ action: a })}>Edit</button><button className="work-secondary" onClick={() => download(a)}><CalendarDays size={15} /> Calendar</button></>}</div>
          </article>)}</div> : <div className="work-empty"><CalendarDays size={32} /><h3>{search || filter !== 'open' ? 'No matching actions' : data.actions.length ? 'All caught up' : 'Your next deadline starts here'}</h3><p>Add a contract, review its extracted deadlines, and confirm an owner. Already uploaded? Open Contracts to create an action.</p><button className="work-primary" onClick={() => data.contracts.length ? setTab('contracts') : onUpload()}>{data.contracts.length ? 'Open contracts' : 'Add your first contract'}</button></div>}
        </>}
        {tab === 'contracts' && (contracts.length ? <div className="work-contracts">{contracts.map(c => <article key={c.id}><div className="work-file-icon"><FileText size={22} /></div><div className="work-contract-info"><h3>{c.filename}</h3><p>{c.contract_type} · {c.total_pages} pages</p><small>{c.deadline_count} extracted date suggestions · {data.actions.filter(a => a.document_id === c.id && a.status === 'open').length} open actions</small></div><div className="work-buttons"><button className="work-secondary" onClick={() => onOpenContract(c)}>{c.analysis_id ? 'Review contract' : 'Analyze contract'}<ArrowUpRight size={14} /></button><button className="work-primary" onClick={() => setEditor({ contract: c })}>Create action</button></div></article>)}</div> : <div className="work-empty"><FileText size={32} /><h3>{search ? 'No matching contracts' : 'A home for every agreement'}</h3><p>Upload vendor and SaaS agreements to keep their deadlines in one place.</p><button className="work-primary" onClick={onUpload}>Add contract</button></div>)}
        {tab === 'reminders' && <><p className="work-callout">Reminders are delivered here at 30, 7, and 1 day before a confirmed deadline, on the due day, and once overdue. Use Calendar on an action for alerts outside this app. No emails are sent.</p>{data.reminders.length ? <div className="work-reminders">{data.reminders.map(r => <article key={r.id} className={r.read_at ? 'is-read' : ''}><Bell size={18} /><div><h3>{r.title}</h3><p>{r.detail}</p><small>{new Date(r.created_at).toLocaleString()}</small></div>{!r.read_at && <button className="work-secondary" onClick={async () => { try { await api.workspace(`/reminders/${r.id}/read`, 'PATCH'); await load(); } catch (err) { setError(err.message); } }}>Mark read</button>}</article>)}</div> : <div className="work-empty"><Bell size={32} /><h3>No reminders yet</h3><p>Confirmed actions appear here when a reminder is due.</p></div>}</>}
      </section>
    </>}
    {editor && <ActionEditor api={api} {...editor} onClose={() => setEditor(null)} onSaved={() => { setEditor(null); setNotice('Action confirmed and saved.'); load(); }} />}
    {detail && <Modal title="Action activity" onClose={() => !busy && setDetail(null)}>
      <h3>{detail.title}</h3><p className="work-muted">{detail.document_name} · {detail.owner} · {detail.due_date}</p>
      {detail.source?.evidence && <blockquote className="work-evidence">Page {detail.source.evidence.page}: “{detail.source.evidence.quote}”</blockquote>}
      <form className="work-form" onSubmit={saveStatus}><label>Record an outcome<select value={status} onChange={e => setStatus(e.target.value)}>{detail.status !== 'completed' && <option value="completed">Completed</option>}{detail.status !== 'cancelled' && <option value="cancelled">Cancelled / no longer needed</option>}{detail.status !== 'open' && <option value="open">Reopen</option>}</select></label><label>Decision / completion evidence<textarea required minLength={5} maxLength={3000} rows={3} placeholder="e.g. Cancellation notice sent to vendor on 12 October; email reference CG-142." value={note} onChange={e => setNote(e.target.value)} /></label>{error && <p role="alert" className="work-error">{error}</p>}<button disabled={busy} className="work-primary">{busy ? 'Saving…' : 'Save outcome'}</button></form>
      <h3 className="work-activity-title">Activity history</h3>{events === null ? <p>Loading activity…</p> : events.map((e, i) => <div className="work-event" key={i}><strong>{e.kind}</strong><time>{new Date(e.created_at).toLocaleString()}</time><p>{eventText(e)}</p></div>)}
    </Modal>}
  </div>;
}
