import React from 'react';
import { FileText, Image as ImageIcon, Trash2, CheckCircle2, User, Calendar } from 'lucide-react';

export default function PrescriptionCard({ prescription, onRemove }) {
  const isPdf = prescription.file_type === 'pdf' || prescription.file_name?.toLowerCase().endsWith('.pdf');

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:shadow-md transition flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="flex items-center space-x-2.5">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
              isPdf ? 'bg-red-50 text-red-600' : 'bg-teal-50 text-teal-600'
            }`}>
              {isPdf ? <FileText className="w-5 h-5" /> : <ImageIcon className="w-5 h-5" />}
            </div>
            <div className="overflow-hidden">
              <h4 className="text-sm font-bold text-slate-900 truncate max-w-[170px]" title={prescription.file_name}>
                {prescription.file_name}
              </h4>
              <span className="text-[11px] font-semibold text-teal-700 uppercase tracking-wider">
                {prescription.file_type || (isPdf ? 'PDF' : 'IMAGE')}
              </span>
            </div>
          </div>

          {onRemove && (
            <button
              onClick={() => onRemove(prescription.id)}
              className="text-slate-400 hover:text-rose-600 p-1 rounded-md hover:bg-rose-50 transition"
              title="Remove prescription"
              aria-label="Remove prescription"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Doctor and Date details */}
        <div className="space-y-1.5 pt-2 border-t border-slate-100 text-xs text-slate-600">
          <div className="flex items-center space-x-1.5">
            <User className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-medium text-slate-800 truncate">
              {prescription.doctor_name || 'Attending Physician'}
            </span>
          </div>
          <div className="flex items-center space-x-1.5">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>{prescription.prescription_date || 'Date not specified'}</span>
          </div>
        </div>
      </div>

      <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
        <span className="flex items-center space-x-1 text-teal-700 font-semibold">
          <CheckCircle2 className="w-3.5 h-3.5 text-teal-600" />
          <span>{prescription.medicines_count || 3} Medicines</span>
        </span>
        <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-[10px] font-bold uppercase">
          {prescription.status || 'Analysed'}
        </span>
      </div>
    </div>
  );
}
