import React from 'react';
import { ShieldAlert, AlertTriangle } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function SafetyBanner({ compact = false }) {
  const { t } = useLanguage();

  if (compact) {
    return (
      <div className="bg-amber-50/90 border-l-4 border-amber-500 p-3 rounded-r-lg shadow-sm">
        <div className="flex items-start space-x-2.5">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <p className="text-xs text-amber-900 leading-relaxed font-medium">
            {t('safety.banner')}
          </p>
        </div>
      </div>
    );
  }

  return (
    <aside aria-label="Medical safety notice" className="bg-gradient-to-r from-amber-50 via-orange-50 to-amber-50 border border-amber-200 rounded-xl p-4 sm:p-5 shadow-sm">
      <div className="flex items-start space-x-3.5">
        <div className="w-9 h-9 rounded-lg bg-amber-500/10 text-amber-700 flex items-center justify-center shrink-0 mt-0.5 border border-amber-300/60">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div className="space-y-1">
          <h2 className="text-xs font-bold uppercase tracking-wider text-amber-800">
            Medication Safety Advisory & Clinical Disclaimer
          </h2>
          <p className="text-sm text-amber-900 leading-relaxed">
            {t('safety.banner')}
          </p>
        </div>
      </div>
    </aside>
  );
}
