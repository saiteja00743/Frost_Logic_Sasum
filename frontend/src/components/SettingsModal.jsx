import React, { useState, useEffect } from 'react';
import { X, Key, Cpu, ShieldCheck, Sparkles, Check } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, onSaveSettings }) {
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
    localStorage.setItem('clauseguard_provider', provider);
    localStorage.setItem('clauseguard_api_key', apiKey.trim());
    localStorage.setItem('clauseguard_model', customModel.trim());
    localStorage.setItem('clauseguard_api_base_url', backendUrl.trim());
    onSaveSettings({
      provider,
      apiKey: apiKey.trim(),
      customModel: customModel.trim(),
      backendUrl: backendUrl.trim(),
    });
    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="w-full max-w-lg rounded-2xl glass-panel border border-slate-700/80 p-6 sm:p-7 shadow-2xl relative">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">AI Engine & API Settings</h3>
              <p className="text-xs text-slate-400">Configure LLM providers or use the local offline engine</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
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
                className={`p-3 rounded-xl border text-left text-xs transition ${
                  provider === 'auto'
                    ? 'border-teal-500/50 bg-teal-500/10 text-teal-300 font-semibold'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-bold text-white mb-0.5">Intelligent Heuristic</div>
                <div className="text-[11px] text-slate-400">Zero latency, offline fallback, 100% free</div>
              </button>

              <button
                type="button"
                onClick={() => setProvider('openrouter')}
                className={`p-3 rounded-xl border text-left text-xs transition ${
                  provider === 'openrouter'
                    ? 'border-teal-500/50 bg-teal-500/10 text-teal-300 font-semibold'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-bold text-white mb-0.5">OpenRouter / Claude</div>
                <div className="text-[11px] text-slate-400">Unified LLM gateway (Recommended)</div>
              </button>

              <button
                type="button"
                onClick={() => setProvider('openai')}
                className={`p-3 rounded-xl border text-left text-xs transition ${
                  provider === 'openai'
                    ? 'border-teal-500/50 bg-teal-500/10 text-teal-300 font-semibold'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-bold text-white mb-0.5">OpenAI (GPT-4o)</div>
                <div className="text-[11px] text-slate-400">Direct OpenAI API key</div>
              </button>

              <button
                type="button"
                onClick={() => setProvider('gemini')}
                className={`p-3 rounded-xl border text-left text-xs transition ${
                  provider === 'gemini'
                    ? 'border-teal-500/50 bg-teal-500/10 text-teal-300 font-semibold'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-bold text-white mb-0.5">Google Gemini</div>
                <div className="text-[11px] text-slate-400">Gemini 2.0 Flash / Pro</div>
              </button>
            </div>
          </div>

          {/* API Key Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
              <span>API Key (Optional)</span>
              <span className="text-[10px] text-slate-400">Saved in browser session</span>
            </label>
            <div className="relative">
              <input
                type="password"
                placeholder={provider === 'auto' ? 'Leave blank to use built-in engine' : 'sk-or-v1-... or sk-...'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full bg-slate-900/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-400"
              />
              <Key className="w-4 h-4 text-slate-500 absolute right-3 top-3 pointer-events-none" />
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              If left blank, ClauseGuard uses its built-in rule-based verification engine.
            </p>
          </div>

          {/* Custom Model */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Custom Model Override (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g. google/gemini-2.0-flash-001 or gpt-4o-mini"
              value={customModel}
              onChange={(e) => setCustomModel(e.target.value)}
              className="w-full bg-slate-900/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-400 font-mono"
            />
          </div>

          {/* Backend API Base URL */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
              <span>Backend API Server URL (Render)</span>
              <span className="text-[10px] text-slate-400">Optional</span>
            </label>
            <input
              type="text"
              placeholder="e.g. https://clauseguard-backend.onrender.com"
              value={backendUrl}
              onChange={(e) => setBackendUrl(e.target.value)}
              className="w-full bg-slate-900/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-400 font-mono"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              If deploying on Vercel separately from Render, paste your Render backend URL here if not set via Vercel env.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2.5 pt-5 mt-5 border-t border-slate-800">
          <button
            type="button"
            onClick={onClose}
            className="px-3.5 py-2 text-xs font-semibold text-slate-400 hover:text-white transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs shadow-lg shadow-teal-500/20 transition"
          >
            {savedSuccess ? (
              <>
                <Check className="w-4 h-4 text-slate-950" />
                <span>Saved!</span>
              </>
            ) : (
              <span>Save Configuration</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
