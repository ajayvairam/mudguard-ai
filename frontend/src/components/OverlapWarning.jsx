import React from 'react';
import { Layers, AlertTriangle } from 'lucide-react';
import VoiceButton from './VoiceButton';

export default function OverlapWarning({ warning }) {
  const narration = `Therapeutic overlap alert. ${warning.description}. ${warning.recommendation}`;

  return (
    <div className="rounded-xl border border-indigo-200 bg-indigo-50/30 p-4 sm:p-5 shadow-xs">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-white shadow-xs">
            <Layers className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-black uppercase tracking-wider bg-indigo-100 text-indigo-900 border border-indigo-300">
                ⚠ {warning.severity || 'MODERATE'}
              </span>
              <span className="text-xs font-bold text-indigo-800 uppercase tracking-wider">
                Therapeutic Overlap
              </span>
            </div>
            <h4 className="text-base font-bold text-slate-900 mt-0.5">
              {warning.medicine_a_name} <span className="text-slate-400 font-normal">&</span> {warning.medicine_b_name}
            </h4>
          </div>
        </div>

        <VoiceButton text={narration} />
      </div>

      <div className="space-y-2 text-sm text-slate-700 pl-1">
        <p className="leading-relaxed font-medium">{warning.description}</p>

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
