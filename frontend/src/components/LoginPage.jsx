import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const { signInWithGoogle } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      await signInWithGoogle();
    } catch (err) {
      setError(err.message || 'Sign-in failed. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="login-root">
      {/* Animated background grid */}
      <div className="login-bg-grid" aria-hidden="true" />

      {/* Floating orbs */}
      <div className="login-orb login-orb-1" aria-hidden="true" />
      <div className="login-orb login-orb-2" aria-hidden="true" />
      <div className="login-orb login-orb-3" aria-hidden="true" />

      <div className="login-card">
        {/* Logo + brand */}
        <div className="login-brand">
          <div className="login-logo" aria-hidden="true">
            <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 3L35 10V20C35 28.28 28.28 35.7 20 37C11.72 35.7 5 28.28 5 20V10L20 3Z"
                fill="url(#shield-grad)" />
              <path d="M13 20L18 25L27 15" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              <defs>
                <linearGradient id="shield-grad" x1="5" y1="3" x2="35" y2="37" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#14b8a6" />
                  <stop offset="1" stopColor="#6366f1" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 className="login-title">ClauseGuard AI</h1>
          <p className="login-subtitle">Automated Legal Intelligence</p>
        </div>

        {/* Feature pills */}
        <div className="login-features">
          {[
            { icon: '🔍', text: 'Evidence-linked risk extraction' },
            { icon: '📋', text: 'Obligation tracking & deadlines' },
            { icon: '📄', text: 'AI-powered clause analysis' },
          ].map(({ icon, text }) => (
            <div key={text} className="login-feature-pill">
              <span className="login-feature-icon">{icon}</span>
              <span>{text}</span>
            </div>
          ))}
        </div>

        {/* Sign-in section */}
        <div className="login-signin-section">
          <p className="login-prompt">Sign in to analyze your contracts</p>

          {error && (
            <div className="login-error" role="alert">
              <span>⚠️</span> {error}
            </div>
          )}

          <button
            id="google-signin-btn"
            className="login-google-btn"
            onClick={handleGoogleLogin}
            disabled={loading}
            aria-label="Sign in with Google"
          >
            {loading ? (
              <span className="login-spinner" aria-hidden="true" />
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
            )}
            <span>{loading ? 'Redirecting…' : 'Continue with Google'}</span>
          </button>

          <p className="login-legal">
            By signing in, you agree that ClauseGuard AI does not constitute legal advice.
            Your documents are private and only visible to you.
          </p>
        </div>
      </div>
    </div>
  );
}
