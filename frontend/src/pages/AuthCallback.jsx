import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../services/supabase';

export default function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    if (supabase) {
      // 1. Check existing session
      supabase.auth.getSession().then(({ data: { session } }) => {
        if (session) {
          navigate('/dashboard');
        } else {
          // 2. Listen for auth state change (e.g. PKCE code exchange completion)
          const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
            if (session) {
              navigate('/dashboard');
            }
          });

          // Timeout safety guard to avoid hanging
          const timer = setTimeout(() => {
            navigate('/dashboard');
          }, 2500);

          return () => {
            clearTimeout(timer);
            subscription?.unsubscribe();
          };
        }
      });
    } else {
      navigate('/dashboard');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="text-center space-y-3">
        <div className="w-10 h-10 border-4 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-sm font-semibold text-slate-700">Verifying Google authentication...</p>
        <p className="text-xs text-slate-500">Redirecting to your dashboard...</p>
      </div>
    </div>
  );
}
