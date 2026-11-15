import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import SafetyBanner from '../components/SafetyBanner';
import InteractionWarning from '../components/InteractionWarning';
import DuplicateWarning from '../components/DuplicateWarning';
import DosageWarning from '../components/DosageWarning';
import OverlapWarning from '../components/OverlapWarning';
import MedicineCard from '../components/MedicineCard';
import VoiceButton from '../components/VoiceButton';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Copy, 
  Gauge, 
  Layers, 
  Pill, 
  FileText, 
  CheckCircle2, 
  ArrowRight,
  Filter,
  Check,
  Volume2
} from 'lucide-react';
import { analysisApi, prescriptionApi } from '../services/api';

export default function Analysis() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterType, setFilterType] = useState('ALL'); // ALL, WARNINGS, DUPLICATES, INTERACTIONS, DOSAGE
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    runAnalysis();
  }, [user?.id]);

  const runAnalysis = async () => {
    setLoading(true);
    setError('');
    const uid = user?.id || 'demo-patient-001';
    try {
      const res = await analysisApi.analyse(uid);
      if (res?.data && res.data.medicines && res.data.medicines.length > 0) {
        setAnalysisData(res.data);
        return;
      }
      // If no medicines found under custom user id, fallback to demo-patient-001
      if (uid !== 'demo-patient-001') {
        const demoRes = await analysisApi.analyse('demo-patient-001');
        if (demoRes?.data && demoRes.data.medicines && demoRes.data.medicines.length > 0) {
          setAnalysisData(demoRes.data);
          return;
        }
      }
      setAnalysisData(res?.data || null);
    } catch (err) {
      console.warn('Primary analysis request failed, attempting fallbacks:', err);
      // Fallback 1: Try demo-patient-001
      if (uid !== 'demo-patient-001') {
        try {
          const demoFallback = await analysisApi.analyse('demo-patient-001');
          if (demoFallback?.data && demoFallback.data.medicines && demoFallback.data.medicines.length > 0) {
            setAnalysisData(demoFallback.data);
            return;
          }
        } catch (fErr) {
          console.warn('Demo fallback failed:', fErr);
        }
      }
      // Fallback 2: Direct proxy fetch
      try {
        const proxyRes = await fetch(`/api/prescriptions/analyse?user_id=${encodeURIComponent(uid)}`, {
          method: 'POST'
        });
        if (proxyRes.ok) {
          const proxyData = await proxyRes.json();
          if (proxyData && proxyData.medicines && proxyData.medicines.length > 0) {
            setAnalysisData(proxyData);
            return;
          }
        }
      } catch (proxyErr) {
        console.warn('Direct proxy fetch failed:', proxyErr);
      }
      setError('Could not complete medication safety analysis. Please check your network or try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmAndProceed = async () => {
    if (!analysisData?.analysis_id) return;
    setConfirming(true);
    const uid = user?.id || 'demo-patient-001';
    try {
      await analysisApi.confirm(analysisData.analysis_id, uid);
      navigate('/medications');
    } catch (err) {
      console.error('Failed to confirm analysis:', err);
      navigate('/medications');
    } finally {
      setConfirming(false);
    }
  };

  const handleMedicineUpdated = (updatedMed) => {
    // Re-run analysis after user correction
    runAnalysis();
  };

  const handleMedicineDeleted = (deletedId) => {
    // Re-run analysis after deletion
    runAnalysis();
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-teal-600 border-t-transparent animate-spin"></div>
        <p className="text-slate-600 font-semibold text-sm">Evaluating clinical safety rules & cross-prescriptions...</p>
      </div>
    );
  }

  if (!analysisData || !analysisData.medicines || analysisData.medicines.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <FileText className="w-12 h-12 text-slate-300 mx-auto" />
        <h2 className="text-xl font-bold text-slate-800">
          {error ? 'Analysis Could Not Be Loaded' : 'No Prescriptions Available to Analyse'}
        </h2>
        <p className="text-slate-500 text-sm">
          {error || 'Please upload your prescriptions first or load the sample prescriptions.'}
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <Link
            to="/prescriptions"
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-teal-600 text-white font-bold text-sm shadow-sm hover:bg-teal-700"
          >
            <span>Go to Upload Page</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <button
            onClick={runAnalysis}
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-sm transition"
          >
            <span>Refresh Analysis</span>
          </button>
        </div>
      </div>
    );
  }

  const { statistics, warnings, medicines, prescriptions } = analysisData;

  const filteredWarnings = warnings.filter(w => {
    if (filterType === 'ALL') return true;
    if (filterType === 'DUPLICATES') return w.analysis_type === 'duplicate';
    if (filterType === 'INTERACTIONS') return w.analysis_type === 'interaction';
    if (filterType === 'DOSAGE') return w.analysis_type === 'dosage_concern' || w.analysis_type === 'conflict';
    if (filterType === 'OVERLAPS') return w.analysis_type === 'overlap';
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-teal-700">Safety Verification</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-0.5">
            {t('analysis.title')}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Identified safety findings across {prescriptions.length} doctor prescription documents.
          </p>
        </div>

        <button
          onClick={handleConfirmAndProceed}
          disabled={confirming}
          className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm shadow-md shadow-teal-600/20 transition disabled:opacity-50"
        >
          <Check className="w-4 h-4 stroke-[3]" />
          <span>{confirming ? "Saving..." : t('analysis.confirm_btn')}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

            <SafetyBanner />

      {/* Regional Voice Overview Banner */}
      <div className="bg-gradient-to-r from-teal-50 via-teal-100/40 to-white rounded-2xl p-4 sm:p-5 border border-teal-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-teal-600 text-white shadow-xs">
            <Volume2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <span>{t('analysis.summary_title')}</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-100 text-teal-800 uppercase tracking-wide">
                Voice Assistant
              </span>
            </h3>
            <p className="text-xs text-slate-600 mt-0.5">
              {statistics.duplicate_count + statistics.interaction_count + statistics.dosage_concern_count + statistics.overlap_count > 0
                ? `Identified ${statistics.duplicate_count + statistics.interaction_count + statistics.dosage_concern_count + statistics.overlap_count} safety alerts across ${statistics.total_medicines} medicines.`
                : `All ${statistics.total_medicines} medicines are verified with no critical cross-prescription warnings.`}
            </p>
          </div>
        </div>

        <VoiceButton
          text={`Medication Safety Summary. Cross-referenced ${statistics.total_prescriptions} prescriptions with ${statistics.total_medicines} medicines. Found ${statistics.duplicate_count} duplicate medicines, ${statistics.interaction_count} potential interactions, ${statistics.dosage_concern_count} dosage alerts, and ${statistics.overlap_count} therapeutic overlaps. Please review all safety warnings with your doctor.`}
          className="px-4 py-2 text-xs bg-teal-600 hover:bg-teal-700 text-white border-teal-700 shadow-xs"
          label={t('analysis.listen_summary')}
        />
      </div>

      {/* Statistics Cards (Section 22) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Prescriptions</div>
          <div className="text-3xl font-black text-slate-900 mt-1">{statistics.total_prescriptions}</div>
          <div className="text-[11px] text-slate-400 mt-0.5">Cross-referenced</div>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Medicines</div>
          <div className="text-3xl font-black text-teal-700 mt-1">{statistics.total_medicines}</div>
          <div className="text-[11px] text-slate-400 mt-0.5">Extracted items</div>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="text-xs font-bold text-amber-700 uppercase tracking-wider">Duplicates</div>
          <div className="text-3xl font-black text-amber-600 mt-1">{statistics.duplicate_count}</div>
          <div className="text-[11px] text-slate-400 mt-0.5">Same active ingredient</div>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="text-xs font-bold text-rose-700 uppercase tracking-wider">Interactions</div>
          <div className="text-3xl font-black text-rose-600 mt-1">{statistics.interaction_count}</div>
          <div className="text-[11px] text-slate-400 mt-0.5">Clinical drug pairs</div>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="text-xs font-bold text-purple-700 uppercase tracking-wider">Dosage Concerns</div>
          <div className="text-3xl font-black text-purple-600 mt-1">{statistics.dosage_concern_count}</div>
          <div className="text-[11px] text-slate-400 mt-0.5">High daily exposure</div>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="text-xs font-bold text-indigo-700 uppercase tracking-wider">Overlaps</div>
          <div className="text-3xl font-black text-indigo-600 mt-1">{statistics.overlap_count}</div>
          <div className="text-[11px] text-slate-400 mt-0.5">Therapeutic class</div>
        </div>
      </div>

      {/* Safety Summary Banner (Section 23) */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-lg space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
          <h3 className="text-lg font-bold flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-teal-400" />
            <span>{t('analysis.summary_title')}</span>
          </h3>
          <span className="text-xs text-slate-400 font-medium">Non-color-dependent labels with full clinical explanation</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80">
            <span className="font-black text-emerald-400 block text-sm">✓ {statistics.clean_medicines_count} Medicines</span>
            <span className="text-slate-300">No major detected concerns</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80">
            <span className="font-black text-amber-400 block text-sm">⚠ {statistics.duplicate_count} Duplicate Items</span>
            <span className="text-slate-300">Shared active ingredient</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80">
            <span className="font-black text-rose-400 block text-sm">⚠ {statistics.interaction_count} Interactions</span>
            <span className="text-slate-300">Pairwise drug conflicts</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80">
            <span className="font-black text-purple-400 block text-sm">⚠ {statistics.dosage_concern_count} Dosage Alerts</span>
            <span className="text-slate-300">High daily limit</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80">
            <span className="font-black text-indigo-400 block text-sm">⚠ {statistics.overlap_count} Class Overlaps</span>
            <span className="text-slate-300">Redundant therapy</span>
          </div>
        </div>
      </div>

      {/* Warnings Feed with Filter Tabs */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-3">
          <div>
            <h3 className="text-lg font-bold text-slate-900">
              Clinical Findings & Warnings ({warnings.length})
            </h3>
            <p className="text-xs text-slate-500">
              Click the <span className="font-bold text-teal-700">[🔊 Listen]</span> button on any card to hear regional-language explanations.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5 text-xs font-semibold">
            {['ALL', 'INTERACTIONS', 'DUPLICATES', 'DOSAGE', 'OVERLAPS'].map((tab) => (
              <button
                key={tab}
                onClick={() => setFilterType(tab)}
                className={`px-3 py-1.5 rounded-lg transition ${
                  filterType === tab
                    ? 'bg-teal-600 text-white shadow-xs'
                    : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {filteredWarnings.length === 0 ? (
          <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-500 text-sm">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
            <p>No warnings in this category.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredWarnings.map((w) => {
              if (w.analysis_type === 'duplicate') {
                return <DuplicateWarning key={w.id} warning={w} />;
              } else if (w.analysis_type === 'interaction') {
                return <InteractionWarning key={w.id} warning={w} />;
              } else if (w.analysis_type === 'dosage_concern' || w.analysis_type === 'conflict') {
                return <DosageWarning key={w.id} warning={w} />;
              } else if (w.analysis_type === 'overlap') {
                return <OverlapWarning key={w.id} warning={w} />;
              }
              return <InteractionWarning key={w.id} warning={w} />;
            })}
          </div>
        )}
      </div>

      {/* User Review & In-Place Editable Medicine Table (Section 24, 25) */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900">
              {t('analysis.review_heading')} ({medicines.length})
            </h3>
            <p className="text-xs text-slate-500">
              Review extracted information. Click the edit icon to correct any OCR extraction errors before generating the final summary.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {medicines.map((med) => (
            <MedicineCard
              key={med.id}
              medicine={med}
              onUpdated={handleMedicineUpdated}
              onDeleted={handleMedicineDeleted}
            />
          ))}
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-xs text-slate-500 max-w-lg">
          By proceeding, you verify that the extracted medicine names match your prescriptions. 
          MediGuard AI will assemble the Proposed Consolidated Medication Summary.
        </p>

        <button
          onClick={handleConfirmAndProceed}
          disabled={confirming}
          className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-black text-base shadow-lg shadow-teal-600/20 transition flex items-center justify-center space-x-2.5 disabled:opacity-50"
        >
          <Check className="w-5 h-5 stroke-[3]" />
          <span>{confirming ? "Saving..." : t('analysis.confirm_btn')}</span>
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
