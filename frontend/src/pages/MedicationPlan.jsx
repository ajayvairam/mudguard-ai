import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import SafetyBanner from '../components/SafetyBanner';
import { 
  FileDown, 
  Clock, 
  AlertCircle, 
  CheckCircle2, 
  Sun, 
  Sunset, 
  Moon, 
  Coffee, 
  BellRing, 
  Calendar,
  Sparkles,
  ArrowLeft
} from 'lucide-react';
import { analysisApi, reminderApi } from '../services/api';

export default function MedicationPlan() {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [planItems, setPlanItems] = useState([]);
  const [analysisId, setAnalysisId] = useState('');
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [scheduling, setScheduling] = useState(false);
  const [scheduleSuccess, setScheduleSuccess] = useState(false);

  useEffect(() => {
    loadPlan();
  }, [user?.id]);

  const loadPlan = async () => {
    setLoading(true);
    const uid = user?.id || 'demo-patient-001';
    try {
      const res = await analysisApi.analyse(uid);
      setPlanItems(res.data?.consolidated_plan || []);
      setAnalysisId(res.data?.analysis_id || 'summary');
    } catch (err) {
      console.error('Failed to load consolidated medication plan:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloading(true);
    const uid = user?.id || 'demo-patient-001';
    try {
      const res = await analysisApi.downloadPdf(analysisId, uid);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `MediGuard_Medication_Summary_${analysisId.slice(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF download error:', err);
      alert('Failed to generate PDF summary.');
    } finally {
      setDownloading(false);
    }
  };

  const handleCreateRemindersFromPlan = async () => {
    setScheduling(true);
    const uid = user?.id || 'demo-patient-001';
    try {
      for (const item of planItems) {
        const slots = item.schedule_slots || ['Morning'];
        for (const slot of slots) {
          let timeStr = '08:00 AM';
          if (slot === 'Afternoon') timeStr = '01:00 PM';
          if (slot === 'Evening') timeStr = '06:00 PM';
          if (slot === 'Night') timeStr = '09:00 PM';

          await reminderApi.create(uid, {
            medicine_name: item.medicine_name,
            dose: item.dosage || '1 tablet',
            time: timeStr,
            frequency: item.frequency || 'once_daily',
            instructions: item.instructions || 'As directed by physician'
          });
        }
      }
      setScheduleSuccess(true);
      setTimeout(() => setScheduleSuccess(false), 4000);
    } catch (err) {
      console.error('Error creating reminders from plan:', err);
    } finally {
      setScheduling(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-teal-600 border-t-transparent animate-spin"></div>
        <p className="text-slate-600 font-semibold text-sm">Synthesizing Consolidated Medication Plan...</p>
      </div>
    );
  }

  // Slot bucketing
  const slotsMap = {
    Morning: [],
    Afternoon: [],
    Evening: [],
    Night: []
  };

  planItems.forEach(item => {
    const slots = item.schedule_slots || ['Morning'];
    slots.forEach(slot => {
      if (slotsMap[slot]) {
        slotsMap[slot].push(item);
      }
    });
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-teal-700">
            <Link to="/analysis" className="hover:underline flex items-center space-x-1">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Analysis</span>
            </Link>
            <span>•</span>
            <span>Step 10: Proposed Medication Review</span>
          </div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-0.5">
            {t('medications.title')}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            {t('medications.subtitle')}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleCreateRemindersFromPlan}
            disabled={scheduling || scheduleSuccess}
            className={`inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl border font-bold text-xs transition shadow-xs ${
              scheduleSuccess
                ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                : 'bg-white hover:bg-slate-50 text-slate-800 border-slate-300'
            }`}
          >
            {scheduleSuccess ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Reminders Scheduled!</span>
              </>
            ) : (
              <>
                <BellRing className="w-4 h-4 text-teal-600" />
                <span>{scheduling ? "Scheduling..." : "Add All to Reminders"}</span>
              </>
            )}
          </button>

          <button
            onClick={handleDownloadPdf}
            disabled={downloading}
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm shadow-md shadow-teal-600/20 transition disabled:opacity-50"
          >
            <FileDown className="w-4 h-4" />
            <span>{downloading ? "Generating PDF..." : t('medications.download_pdf')}</span>
          </button>
        </div>
      </div>

      <SafetyBanner />

      {/* Daily Schedule Timeline (Morning, Afternoon, Evening, Night) */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
          <Calendar className="w-5 h-5 text-teal-600" />
          <span>Daily Administration Schedule</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { slot: "Morning", time: "08:00 AM", icon: Coffee, color: "text-amber-600", bg: "bg-amber-50" },
            { slot: "Afternoon", time: "01:00 PM", icon: Sun, color: "text-orange-600", bg: "bg-orange-50" },
            { slot: "Evening", time: "06:00 PM", icon: Sunset, color: "text-indigo-600", bg: "bg-indigo-50" },
            { slot: "Night", time: "09:00 PM", icon: Moon, color: "text-purple-600", bg: "bg-purple-50" },
          ].map(({ slot, time, icon: Icon, color, bg }) => {
            const meds = slotsMap[slot] || [];
            return (
              <div key={slot} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
                    <div className="flex items-center space-x-2">
                      <div className={`w-8 h-8 rounded-lg ${bg} ${color} flex items-center justify-center`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-sm font-bold text-slate-900">{slot}</div>
                        <div className="text-[11px] text-slate-500 font-medium">{time}</div>
                      </div>
                    </div>
                    <span className="text-xs font-bold text-slate-400">({meds.length})</span>
                  </div>

                  {meds.length === 0 ? (
                    <p className="text-xs text-slate-400 py-4 text-center italic">No scheduled meds</p>
                  ) : (
                    <div className="space-y-2.5">
                      {meds.map((m, idx) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs">
                          <div className="font-bold text-slate-900">{m.medicine_name}</div>
                          <div className="text-[11px] text-slate-600 mt-0.5">{m.dosage} • {m.strength || ''}</div>
                          {m.requires_review && (
                            <span className="inline-block mt-1 text-[10px] font-black uppercase text-rose-700 bg-rose-50 px-1.5 py-0.5 rounded border border-rose-200">
                              Requires Verification
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Consolidated Master Table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="p-5 sm:p-6 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Master Consolidated Medication Register</h3>
            <p className="text-xs text-slate-500">Cross-referenced active drug catalog with clinical review status.</p>
          </div>
          <span className="text-xs font-bold text-teal-700 bg-teal-50 px-3 py-1 rounded-full border border-teal-200">
            {planItems.length} Identified Active Lines
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider">
                <th className="py-3 px-4">Medicine Name</th>
                <th className="py-3 px-4">Strength</th>
                <th className="py-3 px-4">Dose Form</th>
                <th className="py-3 px-4">Frequency</th>
                <th className="py-3 px-4">Prescribed Sources</th>
                <th className="py-3 px-4">Review Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {planItems.map((item, idx) => {
                const needsReview = item.requires_review;
                return (
                  <tr key={idx} className={needsReview ? "bg-rose-50/20" : "hover:bg-slate-50/60"}>
                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      <div>{item.medicine_name}</div>
                      {item.generic_name && (
                        <div className="text-[11px] text-slate-400 font-normal">Active: {item.generic_name}</div>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-medium">{item.strength || '-'}</td>
                    <td className="py-3.5 px-4">{item.dosage || '1 tablet'}</td>
                    <td className="py-3.5 px-4">{item.frequency || '-'}</td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {(item.source_prescriptions || []).join(', ') || 'Prescription'}
                    </td>
                    <td className="py-3.5 px-4">
                      {needsReview ? (
                        <div>
                          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-[10px] font-black uppercase tracking-wider bg-red-100 text-red-900 border border-red-300">
                            <AlertCircle className="w-3 h-3 text-red-600" />
                            <span>REVIEW REQUIRED</span>
                          </span>
                          {item.review_reason && (
                            <p className="text-[10px] text-red-800 mt-1 max-w-xs font-medium leading-tight">
                              {item.review_reason}
                            </p>
                          )}
                        </div>
                      ) : (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-[10px] font-black uppercase tracking-wider bg-emerald-100 text-emerald-900 border border-emerald-300">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          <span>NO MAJOR CONFLICT</span>
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
