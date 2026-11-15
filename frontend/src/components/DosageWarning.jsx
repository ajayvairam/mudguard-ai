import React from 'react';
import { Gauge, AlertOctagon } from 'lucide-react';
import VoiceButton from './VoiceButton';

export default function DosageWarning({ warning }) {
  const isCritical = (warning.severity || '').toUpperCase() === 'CRITICAL';
  const narration = `Dosage concern alert. ${warning.description}. ${warning.recommendation}`;

  return (
    <div className={`rounded-xl border p-4 sm:p-5 shadow-xs ${
      isCritical ? 'border-red-400 bg-red-50/50' : 'border-amber-300 bg-amber-50/40'
    }`}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-white shadow-xs">
            {isCritical ? (
              <AlertOctagon className="w-5 h-5 text-red-600" />
            ) : (
              <Gauge className="w-5 h-5 text-amber-600" />
            )}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-black uppercase tracking-wider border ${
                isCritical ? 'bg-red-100 text-red-900 border-red-300' : 'bg-amber-100 text-amber-900 border-amber-300'
              }`}>
                ⚠ {warning.severity || 'HIGH'}
              </span>
              <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">
                Dosage & Exposure Concern
              </span>
            </div>
            <h4 className="text-base font-bold text-slate-900 mt-0.5">
              {warning.medicine_a_name}
            </h4>
          </div>
        </div>

        <VoiceButton text={narration} />
      </div>

      <div className="space-y-3 text-sm text-slate-700 pl-1">
        <p className="leading-relaxed font-medium">{warning.description}</p>

        {warning.daily_exposure_mg && warning.safe_daily_limit_mg && (
          <div className="bg-white p-3 rounded-lg border border-slate-200 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-slate-500 block">Calculated Daily Exposure:</span>
              <span className="text-base font-black text-rose-600">{warning.daily_exposure_mg} mg / day</span>
            </div>
            <div>
              <span className="text-slate-500 block">Maximum Safe Threshold:</span>
              <span className="text-base font-black text-slate-800">{warning.safe_daily_limit_mg} mg / day</span>
            </div>
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
