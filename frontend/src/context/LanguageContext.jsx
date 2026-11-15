import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

import en from '../i18n/en.json';
import ta from '../i18n/ta.json';
import te from '../i18n/te.json';
import hi from '../i18n/hi.json';
import ml from '../i18n/ml.json';
import kn from '../i18n/kn.json';
import bn from '../i18n/bn.json';
import mr from '../i18n/mr.json';

const dictionaries = { en, ta, te, hi, ml, kn, bn, mr };

export const LANGUAGES = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்' },
  { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు' },
  { code: 'ml', label: 'Malayalam', native: 'മലയാളം' },
  { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা' },
  { code: 'mr', label: 'Marathi', native: 'मराठी' },
];

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [currentLang, setCurrentLang] = useState(() => {
    return localStorage.getItem('mediguard_lang') || 'en';
  });

  const changeLanguage = async (code, userId = null) => {
    setCurrentLang(code);
    localStorage.setItem('mediguard_lang', code);

    // If user is logged in, sync with backend database
    if (userId) {
      try {
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('preferred_language', code);
        const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        await axios.put(`${apiBase}/api/language`, formData);
      } catch (err) {
        console.error('Failed to sync language preference to database:', err);
      }
    }
  };

  // Safe nested translation lookup e.g. t('nav.dashboard')
  const t = (path) => {
    const dict = dictionaries[currentLang] || dictionaries.en;
    const parts = path.split('.');
    let current = dict;
    for (const p of parts) {
      if (current && current[p] !== undefined) {
        current = current[p];
      } else {
        // Fallback to English
        let fallback = dictionaries.en;
        for (const fp of parts) {
          if (fallback && fallback[fp] !== undefined) fallback = fallback[fp];
          else return path;
        }
        return fallback || path;
      }
    }
    return current || path;
  };

  return (
    <LanguageContext.Provider value={{ currentLang, changeLanguage, t, languages: LANGUAGES }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
