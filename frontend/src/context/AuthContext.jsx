import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase, isSupabaseConfigured } from '../services/supabase';

const AuthContext = createContext(null);

// Synthetic guest user for when Supabase is not configured
const GUEST_USER = { id: 'guest', email: 'guest@local', role: 'guest' };

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // ── Guest mode: Supabase not configured ──────────────────────────────────
    if (!isSupabaseConfigured || !supabase) {
      console.warn('[ClauseGuard] Running in guest mode (no Supabase config).');
      setUser(GUEST_USER);
      setSession(null);
      setLoading(false);
      return;
    }

    // ── Normal mode: hydrate from existing Supabase session ──────────────────
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    }).catch(() => {
      // If Supabase call itself errors, fall back to guest
      setUser(GUEST_USER);
      setSession(null);
      setLoading(false);
    });

    // Listen for auth state changes (login, logout, token refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    if (!isSupabaseConfigured || !supabase) {
      console.warn('[ClauseGuard] Supabase not configured — sign-in skipped.');
      return;
    }
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin },
    });
    if (error) throw error;
  };

  const signOut = async () => {
    if (!isSupabaseConfigured || !supabase) {
      console.warn('[ClauseGuard] Supabase not configured — sign-out skipped.');
      return;
    }
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  };

  /** Returns the JWT access token to attach to API requests */
  const getAccessToken = () => session?.access_token ?? null;

  return (
    <AuthContext.Provider value={{ user, session, loading, signInWithGoogle, signOut, getAccessToken, isGuest: !isSupabaseConfigured }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
