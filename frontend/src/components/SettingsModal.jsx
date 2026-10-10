import React, { useState, useEffect } from 'react';
import { X, Key, Cpu, Sparkles, Check, RefreshCw } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, onSaveSettings, hasDocument }) {
  const [provider, setProvider] = useState('auto');
  const [apiKey, setApiKey] = useState('');
  const [customModel, setCustomModel] = useState('');
  const [backendUrl, setBackendUrl] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    const savedProv = localStorage.getItem('clauseguard_provider') || 'auto';
    const savedKey = localStorage.getItem('clauseguard_api_key') || '';
    const savedModel = localStorage.getItem('clauseguard_model') || '';
    const savedUrl = localStorage.getItem('clauseguard_api_base_url') || '';
    setProvider(savedProv);
    setApiKey(savedKey);
    setCustomModel(savedModel);
    setBackendUrl(savedUrl);
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = () => {
    const cleanKey = apiKey.trim();
    const cleanModel = customModel.trim();
    const cleanUrl = backendUrl.trim();

    localStorage.setItem('clauseguard_provider', provider);
    localStorage.setItem('clauseguard_api_key', cleanKey);
    localStorage.setItem('clauseguard_model', cleanModel);
    localStorage.setItem('clauseguard_api_base_url', cleanUrl);

    if (typeof onSaveSettings === 'function') {
      onSaveSettings({
        provider,
        apiKey: cleanKey,
        customModel: cleanModel,
        backendUrl: cleanUrl,
      });
    }

    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      onClose();
    }, 600);
  };

  const getProviderInfo = () => {
    switch (provider) {
      case 'gemini':
        return {
          placeholder: 'AIzaSy... (Free key from aistudio.google.com)',
          defaultModel: 'gemini-2.0-flash',
          help: 'Google Gemini 2.0 Flash is 100% free with no credit card required at aistudio.google.com.',
        };
      case 'openai':
        return {
          placeholder: 'sk-proj-... or sk-...',
          defaultModel: 'gpt-4o-mini',
          help: 'Direct OpenAI GPT-4o Mini (Requires active credit balance in OpenAI account).',
        };
      case 'groq':
        return {
          placeholder: 'gsk_... (Free key from console.groq.com)',
          defaultModel: 'llama-3.3-70b-versatile',
          help: 'Groq Cloud provides ultra-fast inference with Llama 3.3 70B. Get a free API key at console.groq.com.',
        };
      default:
        return {
          placeholder: 'Leave blank for offline heuristic engine',
          defaultModel: 'Rule-based verification engine',
          help: '100% offline rule-based extraction. Zero API key needed.',
        };
    }
  };

  const currentInfo = getProviderInfo();

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="w-full sm:max-w-lg rounded-t-2xl sm:rounded-2xl glass-panel border border-slate-700/80 p-5 sm:p-6 lg:p-7 shadow-2xl relative max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">AI Engine &amp; API Settings</h3>
              <p className="text-xs text-slate-400">Choose your AI provider or use the offline engine</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-4">
          {/* Provider Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">
              Select Processing Engine
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setProvider('auto')}
                className={`p-3 rounded-xl border text-left text-xs transition cursor-pointer ${
                  provider === 'auto'
                    ? 'border-teal-400 bg-teal-500/20 text-teal-200 ring-2 ring-teal-500/40 font-semibold'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-bold text-white mb-0.5">Intelligent Heuristic</div>
                <div className="text-[11px] text-slate-400">Zero latency, offline fallback, free</div>
              </button>

              <button
                type="button"
                onClick={() => setProvider('gemini')}
                className={`p-3 rounded-xl border text-left text-xs transition cursor-pointer ${
                  provider === 'gemini'
                    ? 'border-teal-400 bg-teal-500/20 text-teal-200 ring-2 ring-teal-500/40 font-semibold'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-bold text-white mb-0.5">Google Gemini (Free)</div>
                <div className="text-[11px] text-teal-400 font-medium">Gemini 2.0 Flash (Recommended)</div>
              </button>

              <button
                type="button"
                onClick={() => setProvider('openai')}
                className={`p-3 rounded-xl border text-left text-xs transition cursor-pointer ${
                  provider === 'openai'
                    ? 'border-teal-400 bg-teal-500/20 text-teal-200 ring-2 ring-teal-500/40 font-semibold'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-bold text-white mb-0.5">OpenAI (GPT-4o)</div>
                <div className="text-[11px] text-slate-400">Requires OpenAI balance</div>
              </button>

              <button
                type="button"
                onClick={() => setProvider('groq')}
                className={`p-3 rounded-xl border text-left text-xs transition cursor-pointer ${
                  provider === 'groq'
                    ? 'border-teal-400 bg-teal-500/20 text-teal-200 ring-2 ring-teal-500/40 font-semibold'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-bold text-white mb-0.5">Groq Cloud (Fast)</div>
                <div className="text-[11px] text-teal-400 font-medium">Llama 3.3 70B (Free API)</div>
              </button>
            </div>
          </div>

          {/* API Key Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
              <span>API Key</span>
              <span className="text-[10px] text-teal-400">Stored safely in browser</span>
            </label>
            <div className="relative">
              <input
                type="password"
                placeholder={currentInfo.placeholder}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full bg-slate-900/90 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-400"
              />
              <Key className="w-4 h-4 text-slate-500 absolute right-3 top-3 pointer-events-none" />
            </div>
            <p className="text-[11px] text-slate-400 mt-1.5">
              {currentInfo.help}
            </p>
          </div>

          {/* Custom Model */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
              <span>Model (Default: {currentInfo.defaultModel})</span>
              <span className="text-[10px] text-slate-500">Optional override</span>
            </label>
            <input
              type="text"
              placeholder={`Leave blank to use default (${currentInfo.defaultModel})`}
              value={customModel}
              onChange={(e) => setCustomModel(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-400 font-mono"
            />
          </div>

          {/* Backend API Base URL */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
              <span>Backend API Server URL (Render)</span>
              <span className="text-[10px] text-slate-500">Optional</span>
            </label>
            <input
              type="text"
              placeholder="e.g. https://clauseguard-backend.onrender.com"
              value={backendUrl}
              onChange={(e) => setBackendUrl(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-400 font-mono"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-5 mt-5 border-t border-slate-800">
          <p className="text-[11px] text-slate-400">
            {hasDocument ? '⚡ Will re-analyze active document' : ''}
          </p>
          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 text-xs font-semibold text-slate-400 hover:text-white transition cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs shadow-lg shadow-teal-500/20 transition cursor-pointer"
            >
              {savedSuccess ? (
                <>
                  <Check className="w-4 h-4 text-slate-950" />
                  <span>Applied!</span>
                </>
              ) : hasDocument ? (
                <>
                  <RefreshCw className="w-4 h-4 text-slate-950" />
                  <span>Save &amp; Re-analyze</span>
                </>
              ) : (
                <span>Save Configuration</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
