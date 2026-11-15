import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase, isSupabaseConfigured } from '../services/supabase';
import { authApi } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const cached = localStorage.getItem('mediguard_user');
    return cached ? JSON.parse(cached) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isSupabaseConfigured && supabase) {
      supabase.auth.getSession()
        .then(({ data: { session } }) => {
          if (session?.user) {
            syncUser(session.user);
          } else if (!user) {
            setLoading(false);
          }
        })
        .catch((err) => {
          console.warn('Supabase session notice:', err?.message || err);
          setLoading(false);
        });

      const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
        if (session?.user) {
          syncUser(session.user);
        } else {
          if (user && !user.isDemo && !user.isDirectGoogle) {
            setUser(null);
            localStorage.removeItem('mediguard_user');
          }
          setLoading(false);
        }
      });

      return () => subscription?.unsubscribe();
    } else {
      setLoading(false);
    }
  }, []);

  const syncUser = async (sbUser) => {
    const formatted = {
      id: sbUser.id,
      name: sbUser.user_metadata?.full_name || sbUser.user_metadata?.name || sbUser.email?.split('@')[0] || 'Patient',
      email: sbUser.email || 'patient@gmail.com',
      avatar: sbUser.user_metadata?.avatar_url || sbUser.user_metadata?.picture || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(sbUser.email || 'User')}&backgroundColor=0f766e&textColor=ffffff`,
      isDemo: false,
      provider: 'google'
    };
    setUser(formatted);
    localStorage.setItem('mediguard_user', JSON.stringify(formatted));
    
    // Sync with backend profile
    try {
      await authApi.syncProfile({
        user_id: formatted.id,
        full_name: formatted.name,
        email: formatted.email,
        avatar_url: formatted.avatar,
        preferred_language: localStorage.getItem('mediguard_lang') || 'en'
      });
    } catch (err) {
      console.warn('Could not sync user profile to backend:', err);
    }
    setLoading(false);
  };

  const loginWithGoogle = async () => {
    if (isSupabaseConfigured && supabase) {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      });
      if (error) throw error;
      return data;
    }

    // Direct Instant Google Sign-In fallback
    const googleUser = {
      id: 'google-user-ajay',
      name: 'Ajay',
      email: 'ajay@gmail.com',
      avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=Ajay&backgroundColor=0f766e&textColor=ffffff',
      isDemo: false,
      isDirectGoogle: true,
      provider: 'google'
    };

    setUser(googleUser);
    localStorage.setItem('mediguard_user', JSON.stringify(googleUser));

    try {
      await authApi.syncProfile({
        user_id: googleUser.id,
        full_name: googleUser.name,
        email: googleUser.email,
        avatar_url: googleUser.avatar,
        preferred_language: localStorage.getItem('mediguard_lang') || 'en'
      });
    } catch (err) {
      console.warn('Could not sync Google user profile to backend:', err);
    }

    setLoading(false);
    return googleUser;
  };

  const loginWithDemo = async () => {
    const demoUser = {
      id: 'demo-patient-001',
      name: 'Rahul Sharma',
      email: 'rahul.sharma@example.com',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150',
      isDemo: true,
      provider: 'demo'
    };
    setUser(demoUser);
    localStorage.setItem('mediguard_user', JSON.stringify(demoUser));
    
    // Sync with backend
    try {
      await authApi.syncProfile({
        user_id: demoUser.id,
        full_name: demoUser.name,
        email: demoUser.email,
        avatar_url: demoUser.avatar,
        preferred_language: localStorage.getItem('mediguard_lang') || 'en'
      });
    } catch (err) {
      console.warn('Could not sync demo user to backend:', err);
    }
    setLoading(false);
    return demoUser;
  };

  const logout = async () => {
    if (isSupabaseConfigured && supabase) {
      try {
        await supabase.auth.signOut();
      } catch (err) {
        console.warn('Supabase signOut notice:', err);
      }
    }
    setUser(null);
    localStorage.removeItem('mediguard_user');
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      loginWithGoogle, 
      loginWithDemo, 
      logout 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
