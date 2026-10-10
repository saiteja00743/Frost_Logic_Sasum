export function getApiBase() {
  const custom = typeof window !== 'undefined' ? localStorage.getItem('clauseguard_api_base_url') : '';
  if (custom && custom.trim()) {
    return custom.trim().replace(/\/+$/, '') + '/api';
  }
  const envUrl = import.meta.env.VITE_API_BASE_URL || '';
  return (envUrl ? envUrl.replace(/\/+$/, '') : '') + '/api';
}

/**
 * Build auth headers from an access token.
 * Pass getAccessToken() from useAuth() as the token provider.
 */
function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
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

    async loadSample(sampleKey) {
      const res = await fetch(`${getApiBase()}/sample/load/${sampleKey}`, {
        method: 'POST',
        headers: authHeaders(token()),
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
