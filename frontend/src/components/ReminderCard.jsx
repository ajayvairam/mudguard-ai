import React, { useState } from 'react';
import { Clock, Check, Bell, Trash2, Power } from 'lucide-react';
import { reminderApi } from '../services/api';
import VoiceButton from './VoiceButton';

export default function ReminderCard({ reminder, onCompleted, onDeleted, onToggled }) {
  const [loading, setLoading] = useState(false);
  const isTaken = reminder.today_status === 'taken';

  const handleComplete = async () => {
    if (isTaken || loading) return;
    setLoading(true);
    try {
      await onCompleted(reminder.id);
    } finally {
      setLoading(false);
    }
  };

  const narrationText = `Medication Reminder. Please take ${reminder.medicine_name}, dose ${reminder.dose || '1 dose'}. Scheduled for ${reminder.time}. ${reminder.instructions || 'Take as advised by your doctor.'}`;

  return (
    <div className={`rounded-xl border p-4 transition-all shadow-xs flex flex-col justify-between ${
      isTaken 
        ? 'bg-emerald-50/60 border-emerald-200' 
        : reminder.enabled 
        ? 'bg-white border-slate-200 hover:border-teal-200 hover:shadow-md' 
        : 'bg-slate-50 border-slate-200 opacity-60'
    }`}>
      <div>
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center space-x-2">
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center font-bold text-sm ${
              isTaken ? 'bg-emerald-600 text-white' : 'bg-teal-50 text-teal-700'
            }`}>
              <Clock className="w-4 h-4" />
            </div>
            <div>
              <div className="text-base font-black text-slate-900 tracking-tight">
                {reminder.time}
              </div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                {reminder.frequency?.replace('_', ' ')}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            {onToggled && (
              <button
                onClick={() => onToggled(reminder.id, !reminder.enabled)}
                className={`p-1.5 rounded-md transition ${
                  reminder.enabled ? 'text-teal-600 hover:bg-teal-50' : 'text-slate-400 hover:bg-slate-200'
                }`}
                title={reminder.enabled ? 'Disable reminder' : 'Enable reminder'}
              >
                <Power className="w-3.5 h-3.5" />
              </button>
            )}
            {onDeleted && (
              <button
                onClick={() => onDeleted(reminder.id)}
                className="p-1.5 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
                title="Delete reminder"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>

        <div className="mt-2">
          <h4 className="text-base font-bold text-slate-900">{reminder.medicine_name}</h4>
          <p className="text-xs font-semibold text-teal-700 mt-0.5">Dose: {reminder.dose}</p>
          {reminder.instructions && (
            <p className="text-xs text-slate-600 mt-1 italic">{reminder.instructions}</p>
          )}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
        <VoiceButton
          text={narrationText}
          className="py-1.5 px-2.5 text-[11px]"
        />

        {isTaken ? (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-emerald-100 text-emerald-800 text-xs font-bold">
            <Check className="w-3.5 h-3.5 text-emerald-600 stroke-[3]" />
            <span>Taken</span>
          </span>
        ) : (
          <button
            onClick={handleComplete}
            disabled={loading || !reminder.enabled}
            className="inline-flex items-center justify-center space-x-1 px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition shadow-xs disabled:opacity-50 flex-1"
          >
            <Check className="w-3.5 h-3.5" />
            <span>Mark Taken</span>
          </button>
        )}
      </div>
    </div>
  );
}
