import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { Globe, ChevronDown, Check } from 'lucide-react';

export default function LanguageSelector() {
  const { currentLang, changeLanguage, languages } = useLanguage();
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const selected = languages.find(l => l.code === currentLang) || languages[0];

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium transition shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
        aria-label="Select Language"
        title="Select Preferred Language"
      >
        <Globe className="w-4 h-4 text-teal-600" />
        <span className="font-semibold text-slate-900">{selected.native}</span>
        <span className="text-xs text-slate-400 hidden sm:inline">({selected.label})</span>
        <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 rounded-xl bg-white shadow-xl border border-slate-100 py-1.5 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="px-3 py-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-100">
            Regional Language / மொழி
          </div>
          <div className="max-h-64 overflow-y-auto py-1">
            {languages.map((lang) => {
              const isSelected = lang.code === currentLang;
              return (
                <button
                  key={lang.code}
                  onClick={() => {
                    changeLanguage(lang.code, user?.id);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-3.5 py-2 text-sm text-left transition ${
                    isSelected ? 'bg-teal-50 text-teal-900 font-semibold' : 'text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="text-sm">{lang.native}</span>
                    <span className="text-xs text-slate-400">{lang.label}</span>
                  </div>
                  {isSelected && <Check className="w-4 h-4 text-teal-600" />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
