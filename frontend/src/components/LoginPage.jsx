import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, Sparkles, CheckCircle, ArrowRight, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const { signInWithGoogle, continueAsGuest } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGuestLogin = () => {
    setError(null);
    continueAsGuest();
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      await signInWithGoogle();
    } catch (err) {
      console.warn('Google sign-in attempt:', err);
      setError(
        err.message ||
        'Google Auth is not configured for this deployment. Click "Continue as Guest" to use the app immediately.'
      );
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
      style={{ backgroundColor: 'var(--bg-base)' }}
    >
      {/* Background ambient lighting */}
      <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/3 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        <div className="glass-panel border border-slate-800 rounded-3xl p-7 sm:p-9 shadow-2xl backdrop-blur-xl bg-slate-900/70">
          {/* Brand header */}
          <div className="text-center mb-7">
            <div className="inline-flex items-center justify-center h-14 w-14 rounded-2xl bg-gradient-to-tr from-sky-500 via-teal-400 to-emerald-400 p-[1px] shadow-lg shadow-teal-500/25 mb-4">
              <div className="h-full w-full bg-slate-950 rounded-[15px] flex items-center justify-center">
                <Shield className="w-7 h-7 text-teal-400" />
              </div>
            </div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">ClauseGuard AI</h1>
            <p className="text-xs uppercase tracking-widest font-semibold text-teal-400/90 mt-1">
              Automated Legal Intelligence
            </p>
          </div>

          {/* Feature highlights */}
          <div className="space-y-2 mb-7">
            {[
              { text: 'Evidence-linked risk extraction with page citations' },
              { text: 'Unilateral obligation & deadline detection' },
              { text: 'Instant executive summary & clause review' },
            ].map(({ text }, idx) => (
              <div key={idx} className="flex items-center gap-2.5 text-xs text-slate-300">
                <CheckCircle className="w-3.5 h-3.5 text-teal-400 shrink-0" />
                <span>{text}</span>
              </div>
            ))}
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mb-5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-200 text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div className="flex-1 leading-relaxed">
                <span>{error}</span>
              </div>
            </div>
          )}

          {/* Action buttons */}
          <div className="space-y-3">
            {/* Primary Guest Mode button */}
            <button
              id="guest-access-btn"
              onClick={handleGuestLogin}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-sm shadow-lg shadow-teal-500/20 transition cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-slate-950" />
              <span>Continue as Guest (No Login Required)</span>
              <ArrowRight className="w-4 h-4 text-slate-950" />
            </button>

            {/* Divider */}
            <div className="relative my-4 flex items-center justify-center">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-800" />
              </div>
              <span className="relative bg-slate-900 px-3 text-[10px] uppercase font-semibold text-slate-500 tracking-wider">
                Or optional sign-in
              </span>
            </div>

            {/* Google OAuth Button */}
            <button
              id="google-signin-btn"
              onClick={handleGoogleLogin}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2.5 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-medium text-xs transition cursor-pointer disabled:opacity-60"
            >
              {loading ? (
                <div className="w-4 h-4 rounded-full border-2 border-teal-400 border-t-transparent animate-spin" />
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
              )}
              <span>{loading ? 'Connecting...' : 'Continue with Google'}</span>
            </button>
          </div>

          <p className="text-[11px] text-slate-500 text-center mt-6 leading-relaxed">
            ClauseGuard AI does not constitute legal advice. Your documents remain private to your session.
          </p>
        </div>
      </div>
    </div>
  );
}
