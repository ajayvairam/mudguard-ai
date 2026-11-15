import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import SafetyBanner from '../components/SafetyBanner';
import ReminderCard from '../components/ReminderCard';
import { 
  Bell, 
  Plus, 
  Clock, 
  CheckCircle2, 
  Calendar, 
  History as HistoryIcon,
  X,
  AlertCircle
} from 'lucide-react';
import { reminderApi } from '../services/api';

export default function Reminders() {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [reminders, setReminders] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  const [formData, setFormData] = useState({
    medicine_name: '',
    dose: '1 tablet',
    time: '08:00 AM',
    frequency: 'once_daily',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    instructions: 'Take after meals with water'
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadData();
  }, [user?.id]);

  const loadData = async () => {
    setLoading(true);
    const uid = user?.id || 'demo-patient-001';
    try {
      const [remRes, histRes] = await Promise.all([
        reminderApi.list(uid),
        reminderApi.history(uid)
      ]);
      setReminders(remRes.data || []);
      setHistory(histRes.data || []);
    } catch (err) {
      console.error('Error loading reminders:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReminder = async (e) => {
    e.preventDefault();
    setSaving(true);
    const uid = user?.id || 'demo-patient-001';
    try {
      await reminderApi.create(uid, formData);
      setShowCreateModal(false);
      setFormData({
        medicine_name: '',
        dose: '1 tablet',
        time: '08:00 AM',
        frequency: 'once_daily',
        start_date: new Date().toISOString().split('T')[0],
        end_date: '',
        instructions: 'Take after meals with water'
      });
      await loadData();
    } catch (err) {
      console.error('Failed to create reminder:', err);
      alert('Failed to save reminder.');
    } finally {
      setSaving(false);
    }
  };

  const handleCompleted = async (remId) => {
    const uid = user?.id || 'demo-patient-001';
    try {
      await reminderApi.complete(remId, uid);
      await loadData();
    } catch (err) {
      console.error('Error completing reminder:', err);
    }
  };

  const handleToggled = async (remId, newEnabled) => {
    try {
      await reminderApi.toggle(remId, newEnabled);
      setReminders(prev => prev.map(r => r.id === remId ? { ...r, enabled: newEnabled } : r));
    } catch (err) {
      console.error('Error toggling reminder:', err);
    }
  };

  const handleDeleted = async (remId) => {
    if (!window.confirm("Delete this medication reminder?")) return;
    try {
      await reminderApi.delete(remId);
      setReminders(prev => prev.filter(r => r.id !== remId));
    } catch (err) {
      console.error('Error deleting reminder:', err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-teal-700">Patient Adherence</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-0.5">
            Medication Reminders
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Configure daily dosage alerts and track when each medicine was taken.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm shadow-md shadow-teal-600/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>+ Add Reminder</span>
        </button>
      </div>

      <SafetyBanner compact />

      {/* Active Reminders Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 pb-2">
          <h3 className="text-base font-bold text-slate-900">
            Active Scheduled Reminders ({reminders.length})
          </h3>
          <span className="text-xs text-slate-500">Sorted chronologically</span>
        </div>

        {reminders.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 text-slate-400 text-sm">
            <Bell className="w-10 h-10 mx-auto text-slate-300 mb-2" />
            <p>No active reminders configured.</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-3 text-xs font-bold text-teal-600 hover:underline"
            >
              + Create Your First Reminder
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {reminders.map((rem) => (
              <ReminderCard
                key={rem.id}
                reminder={rem}
                onCompleted={handleCompleted}
                onToggled={handleToggled}
                onDeleted={handleDeleted}
              />
            ))}
          </div>
        )}
      </div>

      {/* Reminder History Log (Section 35) */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <HistoryIcon className="w-5 h-5 text-teal-600" />
          <div>
            <h3 className="text-base font-bold text-slate-900">Adherence Activity Log</h3>
            <p className="text-xs text-slate-500">Record of confirmed doses and medication intake timestamps.</p>
          </div>
        </div>

        {history.length === 0 ? (
          <p className="text-xs text-slate-400 py-4 text-center italic">
            No medication adherence activity recorded yet. Click "Mark as Taken" on any reminder to log doses.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 uppercase font-bold text-[10px]">
                  <th className="py-2.5 px-3">Medication</th>
                  <th className="py-2.5 px-3">Dose</th>
                  <th className="py-2.5 px-3">Scheduled Time</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Recorded At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {history.map((h) => (
                  <tr key={h.id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-bold text-slate-900">{h.medicine_name || 'Medication'}</td>
                    <td className="py-2.5 px-3">{h.dose}</td>
                    <td className="py-2.5 px-3 text-slate-500">{new Date(h.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                    <td className="py-2.5 px-3">
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>Taken</span>
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400">
                      {h.taken_at ? new Date(h.taken_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal: Add Reminder */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">Set Medication Reminder</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateReminder} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Medicine Name</label>
                <input
                  type="text"
                  value={formData.medicine_name}
                  onChange={(e) => setFormData({ ...formData, medicine_name: e.target.value })}
                  placeholder="e.g. Paracetamol 650 mg"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Dose</label>
                  <input
                    type="text"
                    value={formData.dose}
                    onChange={(e) => setFormData({ ...formData, dose: e.target.value })}
                    placeholder="e.g. 1 tablet"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Time</label>
                  <input
                    type="text"
                    value={formData.time}
                    onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                    placeholder="e.g. 08:00 AM"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Frequency</label>
                <select
                  value={formData.frequency}
                  onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                >
                  <option value="once_daily">Once Daily</option>
                  <option value="twice_daily">Twice Daily</option>
                  <option value="three_times_daily">Three Times Daily</option>
                  <option value="four_times_daily">Four Times Daily</option>
                  <option value="as_needed">As Needed (PRN)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Instructions / Meal Guidance</label>
                <input
                  type="text"
                  value={formData.instructions}
                  onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                  placeholder="e.g. After food with full glass of water"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-bold transition shadow-xs"
                >
                  {saving ? "Saving..." : "Save Reminder"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
