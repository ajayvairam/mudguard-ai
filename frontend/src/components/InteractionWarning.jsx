import React from 'react';
import { AlertCircle, AlertTriangle, ShieldAlert, Info } from 'lucide-react';
import VoiceButton from './VoiceButton';

const SEVERITY_CONFIG = {
  CRITICAL: {
    badgeBg: 'bg-red-100',
    badgeText: 'text-red-900 border-red-300',
    cardBorder: 'border-red-300 bg-red-50/40',
    icon: ShieldAlert,
    iconColor: 'text-red-600',
  },
  HIGH: {
    badgeBg: 'bg-rose-100',
    badgeText: 'text-rose-900 border-rose-300',
    cardBorder: 'border-rose-200 bg-rose-50/30',
    icon: AlertCircle,
    iconColor: 'text-rose-600',
  },
  MODERATE: {
    badgeBg: 'bg-amber-100',
    badgeText: 'text-amber-900 border-amber-300',
    cardBorder: 'border-amber-200 bg-amber-50/20',
    icon: AlertTriangle,
    iconColor: 'text-amber-600',
  },
  LOW: {
    badgeBg: 'bg-slate-100',
    badgeText: 'text-slate-800 border-slate-300',
    cardBorder: 'border-slate-200 bg-white',
    icon: Info,
    iconColor: 'text-slate-500',
  }
};

export default function InteractionWarning({ warning }) {
  const sev = (warning.severity || 'MODERATE').toUpperCase();
  const config = SEVERITY_CONFIG[sev] || SEVERITY_CONFIG.MODERATE;
  const Icon = config.icon;

  const narrationText = `Drug Interaction Warning. Severity: ${sev}. Between ${warning.medicine_a_name} and ${warning.medicine_b_name}. ${warning.description}. Recommended action: ${warning.recommendation}`;

  return (
    <div className={`rounded-xl border p-4 sm:p-5 transition-all shadow-xs ${config.cardBorder}`}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-white shadow-xs">
            <Icon className={`w-5 h-5 ${config.iconColor}`} />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-black uppercase tracking-wider border ${config.badgeBg} ${config.badgeText}`}>
                ⚠ {sev}
              </span>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                Drug-Drug Interaction
              </span>
            </div>
            <h4 className="text-base font-bold text-slate-900 mt-0.5">
              {warning.medicine_a_name} <span className="text-slate-400 font-normal">+</span> {warning.medicine_b_name}
            </h4>
          </div>
        </div>

        <VoiceButton text={narrationText} />
      </div>

      <div className="space-y-2.5 text-sm text-slate-700 pl-1">
        <div>
          <span className="font-semibold text-slate-900">Explanation: </span>
          <span className="text-slate-700 leading-relaxed">{warning.description}</span>
        </div>

        {warning.concern && (
          <div className="bg-white/90 p-2.5 rounded-lg border border-slate-200/80 text-xs text-slate-800">
            <span className="font-bold text-rose-700">Clinical Concern: </span>
            {warning.concern}
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

        {warning.source && (
          <div className="text-[11px] text-slate-600 italic pt-1">
            Evidence Source: {warning.source}
          </div>
        )}
      </div>
    </div>
  );
}
