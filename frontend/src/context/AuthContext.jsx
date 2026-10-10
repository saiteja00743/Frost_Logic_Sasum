import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase, isSupabaseConfigured } from '../services/supabase';

const AuthContext = createContext(null);

export const GUEST_USER = {
  id: 'guest',
  email: 'guest@clauseguard.ai',
  user_metadata: { full_name: 'Guest User' },
  role: 'guest',
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1. If user previously selected Guest Mode, or Supabase is not configured:
    const isSavedGuest = localStorage.getItem('clauseguard_guest_session') === 'true';
    if (!isSupabaseConfigured || !supabase || isSavedGuest) {
      setUser(GUEST_USER);
      setSession(null);
      setLoading(false);
      return;
    }

    // 2. Hydrate from Supabase session if configured
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    }).catch(() => {
      // Graceful fallback to guest on any Supabase network/auth error
      setUser(GUEST_USER);
      setSession(null);
      setLoading(false);
    });

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? (localStorage.getItem('clauseguard_guest_session') === 'true' ? GUEST_USER : null));
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const continueAsGuest = () => {
    localStorage.setItem('clauseguard_guest_session', 'true');
    setUser(GUEST_USER);
    setSession(null);
    setLoading(false);
  };

  const signInWithGoogle = async () => {
    if (!isSupabaseConfigured || !supabase) {
      throw new Error(
        'Google Authentication is not configured for this deployment. Please click "Continue as Guest" to use the app immediately.'
      );
    }
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin },
    });
    if (error) throw error;
  };

  const signOut = async () => {
    localStorage.removeItem('clauseguard_guest_session');
    if (isSupabaseConfigured && supabase) {
      try {
        await supabase.auth.signOut();
      } catch (err) {
        console.warn('Supabase sign-out error:', err);
      }
    }
    setUser(null);
    setSession(null);
  };

  /** Returns the JWT access token to attach to API requests */
  const getAccessToken = () => session?.access_token ?? null;

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        loading,
        signInWithGoogle,
        continueAsGuest,
        signOut,
        getAccessToken,
        isGuest: !user || user.id === 'guest',
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
