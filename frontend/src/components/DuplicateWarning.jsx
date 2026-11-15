import React from 'react';
import { Copy, AlertTriangle } from 'lucide-react';
import VoiceButton from './VoiceButton';

export default function DuplicateWarning({ warning }) {
  const narration = `Duplicate Medicine Warning. ${warning.description}. ${warning.recommendation}`;

  return (
    <div className="rounded-xl border border-amber-300 bg-amber-50/40 p-4 sm:p-5 shadow-xs">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-white shadow-xs">
            <Copy className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-black uppercase tracking-wider bg-amber-100 text-amber-900 border border-amber-300">
                ⚠ {warning.severity || 'HIGH'}
              </span>
              <span className="text-xs font-bold text-amber-800 uppercase tracking-wider">
                Duplicate Medicine / Active Ingredient
              </span>
            </div>
            <h4 className="text-base font-bold text-slate-900 mt-0.5">
              {warning.medicine_a_name}
            </h4>
          </div>
        </div>

        <VoiceButton text={narration} />
      </div>

      <div className="space-y-2 text-sm text-slate-700 pl-1">
        <p className="leading-relaxed font-medium">{warning.description}</p>

        {warning.daily_exposure_mg && (
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-md bg-white border border-amber-200 text-xs font-bold text-amber-900">
            <span>Estimated Total Combined Daily Dose:</span>
            <span className="text-sm text-amber-700">{warning.daily_exposure_mg} mg/day</span>
          </div>
        )}

        <div className="bg-white p-3 rounded-lg border border-slate-200 text-xs">
          <span className="font-bold text-teal-800 uppercase tracking-wider block mb-1">
            Recommended Action:
          </span>
          <span className="text-slate-700 font-medium leading-relaxed">
            {warning.recommendation}
          </span>
        </div>
      </div>
    </div>
  );
}
