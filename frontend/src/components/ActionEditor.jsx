import { useEffect, useRef, useState } from 'react';

export function Modal({ title, children, onClose }) {
  const ref = useRef(null);
  useEffect(() => {
    const dialog = ref.current;
    dialog.showModal();
    return () => dialog.close();
  }, []);
  return <dialog ref={ref} className="work-dialog" aria-label={title} onCancel={e => { e.preventDefault(); onClose(); }}>
    <div className="work-dialog-heading"><h2>{title}</h2><button type="button" onClick={onClose} aria-label="Close dialog">×</button></div>
    {children}
  </dialog>;
}

export default function ActionEditor({ api, contract, analysis, deadline, action, onClose, onSaved }) {
  const [form, setForm] = useState({
    title: action?.title || deadline?.title || 'Review vendor renewal',
    owner: action?.owner || '', due_date: action?.due_date || '',
    renewal_date: action?.renewal_date || '', notice_days: action?.notice_days ?? '',
    timezone: action?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    notes: action?.notes || '', confirmed: false,
  });
  const [mode, setMode] = useState(action?.renewal_date ? 'renewal' : 'date');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const update = (key, value) => setForm(f => ({ ...f, [key]: value, confirmed: key === 'confirmed' ? value : false }));
  let calculatedDate = '';
  if (mode === 'renewal' && form.renewal_date && form.notice_days !== '') {
    const d = new Date(`${form.renewal_date}T00:00:00Z`);
    d.setUTCDate(d.getUTCDate() - Number(form.notice_days));
    if (!Number.isNaN(d.valueOf())) calculatedDate = d.toISOString().slice(0, 10);
  }
  const due = mode === 'renewal' ? calculatedDate : form.due_date;
  const source = deadline || action?.source;
  async function save(e) {
    e.preventDefault(); setBusy(true); setError('');
    const body = { ...form, due_date: due,
      renewal_date: mode === 'renewal' ? form.renewal_date : null,
      notice_days: mode === 'renewal' ? Number(form.notice_days) : null };
    try {
      if (action) await api.workspace(`/actions/${action.id}`, 'PUT', { ...body, version: action.version });
      else await api.workspace('/actions', 'POST', { ...body, document_id: contract.id,
        analysis_id: deadline ? analysis.analysis_id : null, deadline_id: deadline?.id || null });
      onSaved();
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <Modal title={action ? 'Edit confirmed action' : 'Confirm a contract action'} onClose={() => !busy && onClose()}>
    <p className="work-muted">{contract?.filename || action?.document_name}</p>
    {source?.evidence && <div className="work-evidence">
      <strong>Source · page {source.evidence.page || 'unknown'}</strong>
      <blockquote>“{source.evidence.quote}”</blockquote>
      <p>Extracted timing: {source.date_or_trigger}</p>
      <p>{source.verification_status === 'verified' ? 'Source text matched. Confirm its meaning and timing below.' : 'Source requires review. Check the original agreement before confirming.'}</p>
    </div>}
    <form onSubmit={save} className="work-form">
      <label>Action<input required minLength={3} maxLength={200} value={form.title} onChange={e => update('title', e.target.value)} /></label>
      <label>Internal owner<input required minLength={2} maxLength={100} placeholder="e.g. Priya · Operations" value={form.owner} onChange={e => update('owner', e.target.value)} /><small>Names record responsibility in your workspace. They do not invite or notify a teammate.</small></label>
      <label>Date basis<select value={mode} onChange={e => { setMode(e.target.value); update('confirmed', false); }}>
        <option value="date">I know the action deadline</option><option value="renewal">Calculate a renewal notice deadline</option>
      </select></label>
      {mode === 'renewal' ? <>
        <div className="work-form-grid">
          <label>Renewal date<input type="date" required value={form.renewal_date} onChange={e => update('renewal_date', e.target.value)} /></label>
          <label>Notice period (calendar days)<input type="number" min="0" max="730" required value={form.notice_days} onChange={e => update('notice_days', e.target.value)} /></label>
        </div>
        <p className="work-callout">Notice deadline: <strong>{calculatedDate || 'Enter both fields'}</strong>. This subtracts calendar days only. For business-day rules or other conditions, use a manually confirmed deadline.</p>
      </> : <label>Action deadline<input type="date" required value={form.due_date} onChange={e => update('due_date', e.target.value)} /></label>}
      <label>Time zone<input required value={form.timezone} onChange={e => update('timezone', e.target.value)} /><small>Reminders use this time zone to determine the due day.</small></label>
      <label>Decision context / instructions<textarea maxLength={3000} rows={3} placeholder="What needs to happen? Note the notice method and recipient from the contract." value={form.notes} onChange={e => update('notes', e.target.value)} /></label>
      <label className="work-check"><input type="checkbox" required checked={form.confirmed} onChange={e => update('confirmed', e.target.checked)} /><span>I checked the source agreement and confirm the owner and deadline.</span></label>
      <p className="work-muted">In-app reminders at 30, 7, and 1 day before the deadline, on the due day, and once overdue. Export to your calendar for alerts outside ClauseGuard.</p>
      {error && <p className="work-error" role="alert">{error}</p>}
      <div className="work-buttons"><button type="button" className="work-secondary" disabled={busy} onClick={onClose}>Cancel</button><button className="work-primary" disabled={busy || !due || !form.confirmed}>{busy ? 'Saving…' : 'Confirm & save action'}</button></div>
    </form>
  </Modal>;
}
