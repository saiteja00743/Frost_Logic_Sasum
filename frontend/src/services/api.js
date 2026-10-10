// Default backend URL — Render deployment
const RENDER_BACKEND_URL = 'https://frost-logic-sasum.onrender.com';

export function getApiBase() {
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

function getGuestId() {
  if (typeof window === 'undefined') return 'guest_default';
  let gid = localStorage.getItem('clauseguard_guest_id');
  if (!gid) {
    gid = 'guest_' + (typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2, 12));
    localStorage.setItem('clauseguard_guest_id', gid);
  }
  return gid;
}

/**
 * Build auth headers from an access token or guest session.
 * Pass getAccessToken() from useAuth() as the token provider.
 */
function authHeaders(token) {
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return { 'X-Guest-ID': getGuestId() };
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
        headers: authHeaders(token()),
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
        headers: authHeaders(token()),
      });
      if (!res.ok) throw new Error('Failed to retrieve document');
      return res.json();
    },

    async analyzeDocument(docId, options = {}) {
      const res = await fetch(`${getApiBase()}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders(token()),
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
        headers: authHeaders(token()),
      });
      if (!res.ok) throw new Error('Failed to retrieve analysis');
      return res.json();
    },

    getReportDownloadUrl(analysisId) {
      // Append token as query param for direct download links
      const t = token();
      const base = `${getApiBase()}/analyses/${analysisId}/report`;
      return t ? `${base}?token=${t}` : base;
    },

    async getHistory() {
      const res = await fetch(`${getApiBase()}/history`, {
        headers: authHeaders(token()),
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
          ...authHeaders(token()),
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
