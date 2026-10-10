import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import HeroUpload from './components/HeroUpload';
import ExecutiveSummaryCard from './components/ExecutiveSummaryCard';
import RiskDashboard from './components/RiskDashboard';
import ObligationsTracker from './components/ObligationsTracker';
import DeadlinesTimeline from './components/DeadlinesTimeline';
import KeyClauses from './components/KeyClauses';
import DocumentViewerModal from './components/DocumentViewerModal';
import SettingsModal from './components/SettingsModal';
import HistoryDrawer from './components/HistoryDrawer';
import LoginPage from './components/LoginPage';
import { createApi, api as healthApi } from './services/api';
import { AlertTriangle, ArrowLeft } from 'lucide-react';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';

// ── Inner app (requires auth context) ─────────────────────────────────────────
function AppInner() {
  const { user, loading: authLoading, getAccessToken } = useAuth();

  // Auth-aware API instance — re-created when token changes
  const api = React.useMemo(() => createApi(getAccessToken), [getAccessToken]);

  const [backendStatus, setBackendStatus] = useState('checking');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [documentData, setDocumentData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);

  // Modals state
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [activeViewerQuote, setActiveViewerQuote] = useState(null);
  const [activeViewerPage, setActiveViewerPage] = useState(1);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Check health on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        await healthApi.getHealth();
        setBackendStatus('online');
      } catch (err) {
        console.warn('Backend connection failed:', err);
        setBackendStatus('offline');
      }
    };
    checkBackend();
  }, []);

  // ── Show loading spinner while Supabase hydrates session ──────────────────
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--bg-base)' }}>
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 rounded-full border-2 border-teal-400 border-t-transparent animate-spin" />
          <p className="text-sm text-slate-400">Loading ClauseGuard AI…</p>
        </div>
      </div>
    );
  }

  // ── Show login page if not authenticated ──────────────────────────────────
  if (!user) {
    return <LoginPage />;
  }

  // ── Authenticated app ─────────────────────────────────────────────────────
  const handleFileUpload = async (file) => {
    setIsLoading(true);
    setErrorMessage(null);
    setLoadingMessage('Uploading and extracting document pages...');

    try {
      const docRes = await api.uploadDocument(file);
      setLoadingMessage(`Extracting ${docRes.total_pages} page(s) with PyMuPDF...`);

      const apiKey = localStorage.getItem('clauseguard_api_key') || null;
      const provider = localStorage.getItem('clauseguard_provider') || 'auto';
      const customModel = localStorage.getItem('clauseguard_model') || null;

      setLoadingMessage('Analyzing risks, obligations, and verifying quotations...');
      const analysis = await api.analyzeDocument(docRes.document_id, { apiKey, provider, customModel });

      const fullDoc = await api.getDocument(docRes.document_id);
      setDocumentData(fullDoc);
      setAnalysisResult(analysis);
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message || 'Failed to process document.');
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const handleSelectSample = async (sampleKey) => {
    setIsLoading(true);
    setErrorMessage(null);
    setLoadingMessage('Loading and analyzing prepared sample agreement...');

    try {
      const apiKey = localStorage.getItem('clauseguard_api_key') || null;
      const provider = localStorage.getItem('clauseguard_provider') || 'auto';
      const customModel = localStorage.getItem('clauseguard_model') || null;

      const analysis = await api.loadSample(sampleKey, { apiKey, provider, customModel });
      const fullDoc = await api.getDocument(analysis.document_id);
      setDocumentData(fullDoc);
      setAnalysisResult(analysis);
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message || 'Failed to load sample agreement.');
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const handleReanalyze = async (settings) => {
    if (!analysisResult?.document_id) return;
    setIsLoading(true);
    setErrorMessage(null);
    const pName = settings?.provider === 'gemini' ? 'Google Gemini' : settings?.provider === 'openai' ? 'OpenAI GPT-4o' : settings?.provider === 'openrouter' ? 'OpenRouter' : 'Intelligent Engine';
    setLoadingMessage(`Re-analyzing document with ${pName}...`);

    try {
      const analysis = await api.analyzeDocument(analysisResult.document_id, {
        apiKey: settings?.apiKey ?? localStorage.getItem('clauseguard_api_key'),
        provider: settings?.provider ?? localStorage.getItem('clauseguard_provider') ?? 'auto',
        customModel: settings?.customModel ?? localStorage.getItem('clauseguard_model'),
      });
      setAnalysisResult(analysis);
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message || 'Failed to re-analyze document.');
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const handleSelectHistoryItem = async (analysisId) => {
    setIsLoading(true);
    setIsHistoryOpen(false);
    setErrorMessage(null);
    setLoadingMessage('Loading saved analysis...');

    try {
      const analysis = await api.getAnalysis(analysisId);
      const fullDoc = await api.getDocument(analysis.document_id);
      setDocumentData(fullDoc);
      setAnalysisResult(analysis);
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message || 'Failed to load saved analysis.');
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const handleInspectQuote = ({ page, quote }) => {
    setActiveViewerPage(page || 1);
    setActiveViewerQuote(quote || null);
    setIsViewerOpen(true);
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setDocumentData(null);
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen flex flex-col font-sans" style={{ backgroundColor: 'var(--bg-base)', color: 'var(--text-primary)' }}>
      <Navbar
        backendStatus={backendStatus}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onReset={handleReset}
        hasAnalysis={!!analysisResult}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Error banner */}
        {errorMessage && (
          <div className="max-w-4xl mx-auto mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs sm:text-sm flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="font-bold">Error encountered: </span>
              <span>{errorMessage}</span>
            </div>
            <button onClick={() => setErrorMessage(null)} className="text-slate-400 hover:text-white text-xs underline">
              Dismiss
            </button>
          </div>
        )}

        {!analysisResult ? (
          <HeroUpload
            onFileUpload={handleFileUpload}
            onSelectSample={handleSelectSample}
            isLoading={isLoading}
            loadingMessage={loadingMessage}
          />
        ) : (
          <div>
            <div className="mb-4">
              <button
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-teal-400 transition cursor-pointer font-medium"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Upload Another Document</span>
              </button>
            </div>

            <ExecutiveSummaryCard
              analysis={analysisResult}
              onOpenViewer={() => { setActiveViewerQuote(null); setIsViewerOpen(true); }}
            />
            <RiskDashboard risks={analysisResult.risks || []} onInspectQuote={handleInspectQuote} />
            <ObligationsTracker
              obligations={analysisResult.obligations || []}
              parties={analysisResult.parties || []}
              onInspectQuote={handleInspectQuote}
            />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <DeadlinesTimeline deadlines={analysisResult.deadlines || []} onInspectQuote={handleInspectQuote} />
              <KeyClauses keyClauses={analysisResult.key_clauses || []} onInspectQuote={handleInspectQuote} />
            </div>
          </div>
        )}
      </main>

      <DocumentViewerModal
        isOpen={isViewerOpen}
        onClose={() => setIsViewerOpen(false)}
        documentData={documentData}
        highlightQuote={activeViewerQuote}
        targetPage={activeViewerPage}
      />
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSaveSettings={handleReanalyze}
        hasDocument={Boolean(analysisResult)}
      />
      <HistoryDrawer isOpen={isHistoryOpen} onClose={() => setIsHistoryOpen(false)} onSelectAnalysis={handleSelectHistoryItem} />

      <footer className="w-full border-t border-slate-800/80 bg-slate-950/60 py-6 text-center text-xs text-slate-500">
        <p>ClauseGuard AI • Built for 36-Hour Hackathon • For human assistance only, does not constitute legal advice.</p>
      </footer>
    </div>
  );
}

// ── Root export wraps everything in providers ──────────────────────────────────
export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppInner />
      </AuthProvider>
    </ThemeProvider>
  );
}
