import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

/**
 * Whether Supabase is properly configured via env vars.
 * If not configured, the app runs in guest mode (no auth wall).
 */
export const isSupabaseConfigured =
  Boolean(supabaseUrl) &&
  supabaseUrl !== 'https://your-project-ref.supabase.co' &&
  Boolean(supabaseAnonKey) &&
  supabaseAnonKey !== 'your-anon-key-here';

if (!isSupabaseConfigured) {
  console.warn(
    '[ClauseGuard] VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY not configured. ' +
    'Running in guest mode — auth is disabled.'
  );
}

// Only create a real client when properly configured to avoid crashes
export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;
