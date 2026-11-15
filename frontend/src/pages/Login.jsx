import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { isSupabaseConfigured } from '../services/supabase';
import SafetyBanner from '../components/SafetyBanner';
import { ShieldCheck, UserCheck, AlertCircle } from 'lucide-react';

export default function Login() {
  const { loginWithGoogle, loginWithDemo, user } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (user) {
    navigate('/dashboard');
    return null;
  }

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      await loginWithGoogle();
      if (!isSupabaseConfigured) {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Google login error:', err);
      setError('Could not complete Google Sign-In: ' + (err.message || 'Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setLoading(true);
    try {
      await loginWithDemo();
      navigate('/dashboard');
    } catch (err) {
      console.error('Demo login error:', err);
      setError('Failed to initialize demo session.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
      <div className="max-w-md w-full space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-teal-600 text-white shadow-lg shadow-teal-600/20 mb-2">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h2 className="text-3xl font-black text-slate-900 tracking-tight">
            Sign In to MediGuard AI
          </h2>
          <p className="text-sm text-slate-600">
            Secure access to your prescriptions, safety analyses, and medication schedules.
          </p>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <p className="font-semibold">{error}</p>
          </div>
        )}

        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-md space-y-4">
          {/* Main Google Sign In Button */}
          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full flex items-center justify-center space-x-3 px-4 py-3.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-800 font-bold text-sm shadow-xs transition hover:shadow-md focus:outline-none focus:ring-2 focus:ring-teal-500 disabled:opacity-50 cursor-pointer active:scale-[0.99]"
          >
            {/* Google G SVG */}
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>{loading ? 'Connecting to Google...' : 'Continue with Google'}</span>
          </button>

          <div className="relative flex py-2 items-center">
            <div className="flex-grow border-t border-slate-200"></div>
            <span className="flex-shrink mx-4 text-xs font-semibold text-slate-400 uppercase">Or test immediately</span>
            <div className="flex-grow border-t border-slate-200"></div>
          </div>

          {/* Instant Demo Login Button */}
          <button
            onClick={handleDemoLogin}
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm shadow-md shadow-teal-600/20 transition disabled:opacity-50 cursor-pointer"
          >
            <UserCheck className="w-4 h-4" />
            <span>Instant Demo Login (1-Click)</span>
          </button>

          <p className="text-[11px] text-slate-500 text-center leading-normal pt-2">
            Connected to live Supabase Cloud database with PostgreSQL & Row Level Security.
          </p>
        </div>

        <SafetyBanner compact />
      </div>
    </div>
  );
}
