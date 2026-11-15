import React, { useState } from 'react';
import { Edit2, Trash2, CheckCircle2, AlertCircle, Save, X } from 'lucide-react';
import { medicineApi } from '../services/api';

export default function MedicineCard({ medicine, onUpdated, onDeleted }) {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    original_name: medicine.original_name || '',
    strength: medicine.strength || '',
    dosage: medicine.dosage || '',
    frequency: medicine.frequency || '',
    duration: medicine.duration || '',
    instructions: medicine.instructions || '',
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await medicineApi.update(medicine.id, formData);
      setIsEditing(false);
      if (onUpdated) onUpdated(res.data);
    } catch (err) {
      console.error('Failed to update medicine:', err);
      alert('Failed to save medicine edits.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Remove '${medicine.original_name}' from analysis?`)) return;
    try {
      await medicineApi.delete(medicine.id);
      if (onDeleted) onDeleted(medicine.id);
    } catch (err) {
      console.error('Failed to delete medicine:', err);
    }
  };

  if (isEditing) {
    return (
      <div className="bg-white rounded-xl border-2 border-teal-500 p-4 shadow-md">
        <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
          <h4 className="text-sm font-bold text-teal-800">Edit Extracted Medicine</h4>
          <button onClick={() => setIsEditing(false)} className="text-slate-400 hover:text-slate-600">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-3 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Medicine Name</label>
            <input
              type="text"
              value={formData.original_name}
              onChange={(e) => setFormData({ ...formData, original_name: e.target.value })}
              className="w-full px-3 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Strength (e.g. 500 mg)</label>
              <input
                type="text"
                value={formData.strength}
                onChange={(e) => setFormData({ ...formData, strength: e.target.value })}
                className="w-full px-3 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Dose (e.g. 1 tablet)</label>
              <input
                type="text"
                value={formData.dosage}
                onChange={(e) => setFormData({ ...formData, dosage: e.target.value })}
                className="w-full px-3 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Frequency</label>
              <input
                type="text"
                value={formData.frequency}
                onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                className="w-full px-3 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Duration</label>
              <input
                type="text"
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                className="w-full px-3 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Instructions</label>
            <input
              type="text"
              value={formData.instructions}
              onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
              className="w-full px-3 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-100 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-semibold shadow-xs"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{saving ? 'Saving...' : 'Save Changes'}</span>
            </button>
          </div>
        </form>
      </div>
    );
  }

  const needsVerification = medicine.requires_verification || medicine.confidence < 0.85;

  return (
    <div className={`bg-white rounded-xl border p-4 shadow-xs hover:shadow-md transition flex flex-col justify-between ${
      needsVerification ? 'border-amber-300 bg-amber-50/20' : 'border-slate-200'
    }`}>
      <div>
        <div className="flex items-start justify-between gap-2 mb-2">
          <div>
            <div className="flex items-center space-x-2">
              <h4 className="text-base font-bold text-slate-900">{medicine.original_name}</h4>
              {needsVerification && (
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-100 text-amber-900 border border-amber-300">
                  <AlertCircle className="w-3 h-3" />
                  <span>Verify</span>
                </span>
              )}
            </div>

            <div className="text-xs text-slate-500 font-medium mt-0.5">
              <span>Generic: </span>
              <span className="font-semibold text-slate-700">{medicine.generic_name || medicine.active_ingredient || 'Standard Formulation'}</span>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={() => setIsEditing(true)}
              className="p-1.5 text-slate-400 hover:text-teal-600 rounded-md hover:bg-teal-50 transition"
              title="Edit extracted information"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleDelete}
              className="p-1.5 text-slate-400 hover:text-rose-600 rounded-md hover:bg-rose-50 transition"
              title="Delete medicine"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Medicine Attributes Grid */}
        <div className="grid grid-cols-2 gap-2 mt-3 text-xs bg-slate-50/80 p-2.5 rounded-lg border border-slate-100">
          <div>
            <span className="text-slate-400 block text-[10px] uppercase font-bold">Strength</span>
            <span className="font-semibold text-slate-800">{medicine.strength || '-'}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase font-bold">Dose Form</span>
            <span className="font-semibold text-slate-800">{medicine.dosage || '1 tablet'}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase font-bold">Frequency</span>
            <span className="font-semibold text-slate-800">{medicine.frequency || 'once daily'}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase font-bold">Duration</span>
            <span className="font-semibold text-slate-800">{medicine.duration || '-'}</span>
          </div>
        </div>

        {medicine.instructions && (
          <div className="mt-2 text-xs text-slate-600">
            <span className="font-semibold text-slate-700">Instructions: </span>
            <span>{medicine.instructions}</span>
          </div>
        )}
      </div>

      <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
        <span>From: <strong className="text-slate-700">{medicine.doctor_name || 'Prescription'}</strong></span>
        <span className="text-teal-700 font-semibold">OCR: {Math.round((medicine.confidence || 0.95) * 100)}%</span>
      </div>
    </div>
  );
}
