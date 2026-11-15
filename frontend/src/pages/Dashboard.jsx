import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import SafetyBanner from '../components/SafetyBanner';
import ReminderCard from '../components/ReminderCard';
import { 
  FileText, 
  Pill, 
  AlertTriangle, 
  Copy, 
  Gauge, 
  Bell, 
  Plus, 
  Sparkles, 
  ArrowRight,
  CheckCircle2,
  Calendar
} from 'lucide-react';
import { prescriptionApi, reminderApi, analysisApi } from '../services/api';

export default function Dashboard() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [stats, setStats] = useState({
    prescriptions: 0,
    medicines: 0,
    interactions: 0,
    duplicates: 0,
    dosageConcerns: 0,
    reminders: 0
  });
  const [todayReminders, setTodayReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingSamples, setLoadingSamples] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, [user?.id]);

  const loadDashboardData = async () => {
    setLoading(true);
    const uid = user?.id || 'demo-patient-001';
    try {
      // 1. Prescriptions
      const rxRes = await prescriptionApi.list(uid);
      const rxList = rxRes.data || [];
      const totalMeds = rxList.reduce((acc, r) => acc + (r.medicines_count || 0), 0);

      // 2. Reminders
      const remRes = await reminderApi.list(uid);
      const remList = remRes.data || [];

      // 3. Check for analysis warnings if available
      let interCount = 0;
      let dupCount = 0;
      let doseCount = 0;

      if (rxList.length > 0) {
        try {
          const analysisRes = await analysisApi.analyse(uid);
          const st = analysisRes.data?.statistics;
          if (st) {
            interCount = st.interaction_count || 0;
            dupCount = st.duplicate_count || 0;
            doseCount = st.dosage_concern_count || 0;
          }
        } catch (err) {
          // No analysis yet
        }
      }

      setStats({
        prescriptions: rxList.length,
        medicines: totalMeds,
        interactions: interCount,
        duplicates: dupCount,
        dosageConcerns: doseCount,
        reminders: remList.length
      });

      setTodayReminders(remList);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSamples = async () => {
    setLoadingSamples(true);
    const uid = user?.id || 'demo-patient-001';
    try {
      await prescriptionApi.loadSamples(uid);
      // Create initial sample reminders
      await reminderApi.create(uid, {
        medicine_name: "Atorvastatin 20 mg",
        dose: "1 tablet",
        time: "08:00 AM",
        frequency: "once_daily",
        instructions: "Take with breakfast"
      });
      await reminderApi.create(uid, {
        medicine_name: "Dolo 650",
        dose: "1 tablet",
        time: "01:00 PM",
        frequency: "twice_daily",
        instructions: "Take after lunch"
      });
      await loadDashboardData();
      navigate('/analysis');
    } catch (err) {
      console.error('Failed to load sample prescriptions:', err);
    } finally {
      setLoadingSamples(false);
    }
  };

  const handleCompleteReminder = async (remId) => {
    const uid = user?.id || 'demo-patient-001';
    try {
      await reminderApi.complete(remId, uid);
      setTodayReminders(prev => prev.map(r => r.id === remId ? { ...r, today_status: 'taken' } : r));
    } catch (err) {
      console.error('Failed to mark reminder as taken:', err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-teal-700">Patient Dashboard</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-0.5">
            {t('dashboard.welcome')}, {user?.name || 'Patient'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Review cross-prescription safety alerts and track your daily medication schedule.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to="/prescriptions"
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm shadow-md shadow-teal-600/20 transition"
          >
            <Plus className="w-4 h-4" />
            <span>{t('dashboard.upload_btn')}</span>
          </Link>
        </div>
      </div>

      {/* Safety Notice Banner */}
      <SafetyBanner />

      {/* Main Analysis Call to Action Card */}
      <div className="bg-gradient-to-br from-teal-700 via-teal-800 to-slate-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="max-w-2xl relative z-10 space-y-4">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur text-teal-200 text-xs font-bold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Dual Clinical Safety Engine</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-black tracking-tight leading-snug">
            {t('dashboard.cta_title')}
          </h2>

          <p className="text-sm sm:text-base text-teal-100/90 leading-relaxed">
            {t('dashboard.cta_desc')}
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Link
              to="/prescriptions"
              className="px-6 py-3 rounded-xl bg-white text-teal-900 font-bold text-sm shadow-md hover:bg-teal-50 transition inline-flex items-center space-x-2"
            >
              <span>{t('dashboard.upload_btn')}</span>
              <ArrowRight className="w-4 h-4 text-teal-800" />
            </Link>

            {stats.prescriptions === 0 && (
              <button
                onClick={handleLoadSamples}
                disabled={loadingSamples}
                className="px-5 py-3 rounded-xl bg-teal-900/60 hover:bg-teal-900 text-white border border-teal-500/40 font-semibold text-sm transition inline-flex items-center space-x-2"
              >
                <Sparkles className="w-4 h-4 text-teal-300" />
                <span>{loadingSamples ? "Loading..." : t('dashboard.load_samples')}</span>
              </button>
            )}

            {stats.prescriptions > 0 && (
              <Link
                to="/analysis"
                className="px-5 py-3 rounded-xl bg-teal-600/80 hover:bg-teal-600 text-white font-semibold text-sm transition inline-flex items-center space-x-2"
              >
                <span>View Full Analysis Results</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Statistics Cards Grid (Section 8) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          { label: t('dashboard.stat_prescriptions'), count: stats.prescriptions, icon: FileText, color: "text-blue-600", bg: "bg-blue-50" },
          { label: t('dashboard.stat_medicines'), count: stats.medicines, icon: Pill, color: "text-teal-600", bg: "bg-teal-50" },
          { label: t('dashboard.stat_interactions'), count: stats.interactions, icon: AlertTriangle, color: "text-rose-600", bg: "bg-rose-50" },
          { label: t('dashboard.stat_duplicates'), count: stats.duplicates, icon: Copy, color: "text-amber-600", bg: "bg-amber-50" },
          { label: t('dashboard.stat_dosage'), count: stats.dosageConcerns, icon: Gauge, color: "text-purple-600", bg: "bg-purple-50" },
          { label: t('dashboard.stat_reminders'), count: stats.reminders, icon: Bell, color: "text-emerald-600", bg: "bg-emerald-50" },
        ].map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs">
              <div className={`w-9 h-9 rounded-xl ${card.bg} ${card.color} flex items-center justify-center mb-3`}>
                <Icon className="w-5 h-5" />
              </div>
              <div className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
                {card.count}
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1 leading-tight">
                {card.label}
              </div>
            </div>
          );
        })}
      </div>

      {/* Today's Medication Schedule (Section 34) */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
              <Calendar className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">{t('dashboard.today_schedule')}</h3>
              <p className="text-xs text-slate-500">Track medication adherence and mark doses as taken.</p>
            </div>
          </div>

          <Link to="/reminders" className="text-xs font-bold text-teal-600 hover:text-teal-800">
            Manage All Reminders →
          </Link>
        </div>

        {todayReminders.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-sm">
            <Bell className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p>{t('dashboard.no_reminders')}</p>
            <Link to="/reminders" className="text-xs font-bold text-teal-600 mt-2 inline-block">
              + Create Medication Reminder
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {todayReminders.slice(0, 6).map((rem) => (
              <ReminderCard
                key={rem.id}
                reminder={rem}
                onCompleted={handleCompleteReminder}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
