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
import { api } from './services/api';
import { AlertTriangle, ArrowLeft } from 'lucide-react';
import { ThemeProvider } from './context/ThemeContext';

export default function App() {
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
        await api.getHealth();
        setBackendStatus('online');
      } catch (err) {
        console.warn('Backend connection failed:', err);
        setBackendStatus('offline');
      }
    };
    checkBackend();
  }, []);

  const handleFileUpload = async (file) => {
    setIsLoading(true);
    setErrorMessage(null);
    setLoadingMessage('Uploading and extracting document pages...');

    try {
      // 1. Upload & Extract
      const docRes = await api.uploadDocument(file);
      setLoadingMessage(`Extracting ${docRes.total_pages} page(s) with PyMuPDF...`);

      // 2. Retrieve options from localStorage
      const apiKey = localStorage.getItem('clauseguard_api_key') || null;
      const provider = localStorage.getItem('clauseguard_provider') || 'auto';
      const customModel = localStorage.getItem('clauseguard_model') || null;

      setLoadingMessage('Analyzing risks, obligations, and verifying quotations...');
      const analysis = await api.analyzeDocument(docRes.document_id, {
        apiKey,
        provider,
        customModel,
      });

      // 3. Fetch full document text for viewer
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
      const analysis = await api.loadSample(sampleKey);
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
    <ThemeProvider>
    <div className="min-h-screen flex flex-col font-sans" style={{ backgroundColor: 'var(--bg-base)', color: 'var(--text-primary)' }}>
      {/* Top Navbar */}
      <Navbar
        backendStatus={backendStatus}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onReset={handleReset}
        hasAnalysis={!!analysisResult}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Error notification banner */}
        {errorMessage && (
          <div className="max-w-4xl mx-auto mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs sm:text-sm flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="font-bold">Error encountered: </span>
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-slate-400 hover:text-white text-xs underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* View 1: Upload & Hero (when no active analysis) */}
        {!analysisResult ? (
          <HeroUpload
            onFileUpload={handleFileUpload}
            onSelectSample={handleSelectSample}
            isLoading={isLoading}
            loadingMessage={loadingMessage}
          />
        ) : (
          /* View 2: Complete Analysis Dashboard */
          <div>
            {/* Back button */}
            <div className="mb-4">
              <button
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-teal-400 transition cursor-pointer font-medium"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Upload Another Document</span>
              </button>
            </div>

            {/* Executive Summary & Risk Gauge */}
            <ExecutiveSummaryCard
              analysis={analysisResult}
              onOpenViewer={() => {
                setActiveViewerQuote(null);
                setIsViewerOpen(true);
              }}
            />

            {/* Differentiator 1: Evidence-Linked Risk Analysis */}
            <RiskDashboard
              risks={analysisResult.risks || []}
              onInspectQuote={handleInspectQuote}
            />

            {/* Differentiator 2: Obligations Tracker */}
            <ObligationsTracker
              obligations={analysisResult.obligations || []}
              parties={analysisResult.parties || []}
              onInspectQuote={handleInspectQuote}
            />

            {/* Key Clauses & Deadlines */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <DeadlinesTimeline
                deadlines={analysisResult.deadlines || []}
                onInspectQuote={handleInspectQuote}
              />
              <KeyClauses
                keyClauses={analysisResult.key_clauses || []}
                onInspectQuote={handleInspectQuote}
              />
            </div>
          </div>
        )}
      </main>

      {/* Modals & Drawers */}
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
        onSaveSettings={() => {}}
      />

      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectAnalysis={handleSelectHistoryItem}
      />

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/80 bg-slate-950/60 py-6 text-center text-xs text-slate-500">
        <p>ClauseGuard AI • Built for 36-Hour Hackathon • For human assistance only, does not constitute legal advice.</p>
      </footer>
    </div>
    </ThemeProvider>
  );
}
