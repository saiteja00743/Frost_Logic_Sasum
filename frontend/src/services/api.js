// Default backend URL — Render deployment
const RENDER_BACKEND_URL = 'https://frost-logic-sasum.onrender.com';

export function getApiBase() {
  if (import.meta.env.DEV) return '/api';
  // 1. User-configured URL from Settings modal takes highest priority
  const custom = typeof window !== 'undefined' ? localStorage.getItem('clauseguard_api_base_url') : '';
  if (custom && custom.trim()) {
    return custom.trim().replace(/\/+$/, '') + '/api';
  }
  // 2. Build-time env variable (set in Vercel dashboard as VITE_API_BASE_URL)
  const envUrl = import.meta.env.VITE_API_BASE_URL || '';
  if (envUrl && envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '') + '/api';
  }
  // 3. Hardcoded Render fallback
  return RENDER_BACKEND_URL + '/api';
}

let demoPromise;
async function demoToken() {
  const saved = JSON.parse(localStorage.getItem('clauseguard_demo_session') || 'null');
  if (saved?.access_token && Date.parse(saved.expires_at) > Date.now()) return saved.access_token;
  if (!demoPromise) {
    demoPromise = fetch(`${getApiBase()}/session/demo`, { method: 'POST' })
      .then(async res => {
        if (!res.ok) throw new Error('Demo is unavailable. Please sign in to your account.');
        const session = await res.json();
        localStorage.setItem('clauseguard_demo_session', JSON.stringify(session));
        return session.access_token;
      }).finally(() => { demoPromise = null; });
  }
  return demoPromise;
}
async function authHeaders(token) {
  return { Authorization: `Bearer ${token || await demoToken()}` };
}
async function downloadBlob(res, filename) {
  if (!res.ok) throw new Error('Download failed. Refresh your session and try again.');
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement('a'); a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function createApi(getToken) {
  const token = () => (typeof getToken === 'function' ? getToken() : null);

  return {
    async getHealth() {
      const res = await fetch(`${getApiBase()}/health`);
      if (!res.ok) throw new Error('Failed to fetch backend health');
      return res.json();
    },

    async uploadDocument(file) {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${getApiBase()}/documents`, {
        method: 'POST',
        headers: await authHeaders(token()),
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to upload document');
      }
      return res.json();
    },

    async getDocument(docId) {
      const res = await fetch(`${getApiBase()}/documents/${docId}`, {
        headers: await authHeaders(token()),
      });
      if (!res.ok) throw new Error('Failed to retrieve document');
      return res.json();
    },

    async analyzeDocument(docId, options = {}) {
      const res = await fetch(`${getApiBase()}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...await authHeaders(token()),
        },
        body: JSON.stringify({
          document_id: docId,
          api_key: options.apiKey || null,
          provider: options.provider || 'auto',
          custom_model: options.customModel || null,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Analysis request failed');
      }
      return res.json();
    },

    async getAnalysis(analysisId) {
      const res = await fetch(`${getApiBase()}/analyses/${analysisId}`, {
        headers: await authHeaders(token()),
      });
      if (!res.ok) throw new Error('Failed to retrieve analysis');
      return res.json();
    },

    async downloadReport(analysisId) {
      const res = await fetch(`${getApiBase()}/analyses/${analysisId}/report`, { headers: await authHeaders(token()) });
      return downloadBlob(res, 'ClauseGuard-report.pdf');
    },
    async workspace(path = '/workspace', method = 'GET', body) {
      const res = await fetch(`${getApiBase()}${path}`, {
        method, headers: { 'Content-Type': 'application/json', ...await authHeaders(token()) },
        body: body ? JSON.stringify(body) : undefined,
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        if (res.status === 401 && !token()) localStorage.removeItem('clauseguard_demo_session');
        throw new Error(typeof error.detail === 'string' ? error.detail : 'Please check the form fields and try again.');
      }
      return res.json();
    },
    async downloadCalendar(actionId) {
      const res = await fetch(`${getApiBase()}/actions/${actionId}/calendar`, { headers: await authHeaders(token()) });
      return downloadBlob(res, 'contract-deadline.ics');
    },

    async getHistory() {
      const res = await fetch(`${getApiBase()}/history`, {
        headers: await authHeaders(token()),
      });
      if (!res.ok) throw new Error('Failed to fetch history');
      return res.json();
    },

    async getSamples() {
      const res = await fetch(`${getApiBase()}/samples`);
      if (!res.ok) throw new Error('Failed to fetch sample contracts');
      return res.json();
    },

    async loadSample(sampleKey, options = {}) {
      const res = await fetch(`${getApiBase()}/sample/load/${sampleKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...await authHeaders(token()),
        },
        body: JSON.stringify({
          api_key: options.apiKey || null,
          provider: options.provider || 'auto',
          custom_model: options.customModel || null,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to load sample agreement');
      }
      return res.json();
    },
  };
}

// Legacy singleton for backwards compat (no auth — will get 401 from protected routes)
export const api = createApi(null);
