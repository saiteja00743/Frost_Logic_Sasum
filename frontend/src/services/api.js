const API_BASE = (import.meta.env.VITE_API_BASE_URL || '') + '/api';

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to fetch backend health');
    return res.json();
  },

  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/documents`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload document');
    }
    return res.json();
  },

  async getDocument(docId) {
    const res = await fetch(`${API_BASE}/documents/${docId}`);
    if (!res.ok) throw new Error('Failed to retrieve document');
    return res.json();
  },

  async analyzeDocument(docId, options = {}) {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
    const res = await fetch(`${API_BASE}/analyses/${analysisId}`);
    if (!res.ok) throw new Error('Failed to retrieve analysis');
    return res.json();
  },

  getReportDownloadUrl(analysisId) {
    return `${API_BASE}/analyses/${analysisId}/report`;
  },

  async getHistory() {
    const res = await fetch(`${API_BASE}/history`);
    if (!res.ok) throw new Error('Failed to fetch history');
    return res.json();
  },

  async getSamples() {
    const res = await fetch(`${API_BASE}/samples`);
    if (!res.ok) throw new Error('Failed to fetch sample contracts');
    return res.json();
  },

  async loadSample(sampleKey) {
    const res = await fetch(`${API_BASE}/sample/load/${sampleKey}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to load sample agreement');
    }
    return res.json();
  },
};
