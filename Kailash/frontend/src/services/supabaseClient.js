/**
 * Supabase client for the serverless Go4Garage dashboard.
 *
 * "Backend Supabase": the dashboard reads its figures straight from Supabase
 * Postgres (table public.g4g_dashboard) and authenticates with Supabase Auth —
 * no application server. The confidential figures are protected by Row-Level
 * Security: the publishable key below is public by design (like a Firebase
 * apiKey), and RLS returns rows only to the authorised, signed-in owner.
 *
 * Config comes from build-time env (frontend/.env.production):
 *   REACT_APP_SUPABASE_URL, REACT_APP_SUPABASE_ANON_KEY
 */
import { createClient } from '@supabase/supabase-js';

const url = process.env.REACT_APP_SUPABASE_URL || '';
const anonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || '';

export const supabaseConfigured = Boolean(url && anonKey);

// Persist the session so a reload keeps the user signed in.
export const supabase = createClient(url, anonKey, {
  auth: { persistSession: true, autoRefreshToken: true },
});

export default supabase;
