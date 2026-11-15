import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import SafetyBanner from '../components/SafetyBanner';
import PrescriptionCard from '../components/PrescriptionCard';
import AnalysisProgress from '../components/AnalysisProgress';
import { 
  Upload, 
  FileText, 
  Sparkles, 
  Trash2, 
  ArrowRight, 
  AlertCircle,
  PlusCircle,
  Files
} from 'lucide-react';
import { prescriptionApi } from '../services/api';

export default function UploadPrescription() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [existingPrescriptions, setExistingPrescriptions] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPrescriptions();
  }, [user?.id]);

  const loadPrescriptions = async () => {
    const targetUserId = user?.id || 'demo-patient-001';
    try {
      const res = await prescriptionApi.list(targetUserId);
      setExistingPrescriptions(res.data || []);
    } catch (err) {
      console.error('Failed to load prescriptions, trying fallback fetch:', err);
      try {
        const fallbackRes = await fetch(`/api/prescriptions?user_id=${encodeURIComponent(targetUserId)}`);
        if (fallbackRes.ok) {
          const data = await fallbackRes.json();
          setExistingPrescriptions(data || []);
          return;
        }
      } catch (fallbackErr) {
        console.error('Fallback list failed:', fallbackErr);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setSelectedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      setSelectedFiles(prev => [...prev, ...droppedFiles]);
    }
  };

  const removeSelectedFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleRemoveExisting = async (id) => {
    if (!window.confirm("Remove this prescription?")) return;
    try {
      await prescriptionApi.delete(id);
      setExistingPrescriptions(prev => prev.filter(p => p.id !== id));
    } catch (err) {
      console.error('Failed to delete prescription:', err);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (selectedFiles.length === 0 && existingPrescriptions.length === 0) {
      setError('Please select or upload at least one prescription file first.');
      return;
    }

    setError('');
    setAnalyzing(true);
    const targetUserId = user?.id || 'demo-patient-001';

    try {
      if (selectedFiles.length > 0) {
        await prescriptionApi.upload(targetUserId, selectedFiles);
        setSelectedFiles([]);
      }
      // Start analysis computation immediately in parallel while the progress animation displays
      analysisApi.analyse(targetUserId).catch((err) => {
        console.warn('Pre-warm analysis error:', err);
      });
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to process prescription files. Please verify file format and try again.');
      setAnalyzing(false);
    }
  };

  const handleLoadSamples = async () => {
    setLoading(true);
    setError('');
    const targetUserId = user?.id || 'demo-patient-001';
    try {
      await prescriptionApi.loadSamples(targetUserId);
      await loadPrescriptions();
      // Pre-run analysis in parallel so navigating to /analysis is instantaneous
      analysisApi.analyse(targetUserId).catch((err) => {
        console.warn('Pre-warm sample analysis:', err);
      });
    } catch (err) {
      console.warn('Axios loadSamples error, attempting proxy fallback fetch:', err);
      try {
        const fallbackRes = await fetch(`/api/prescriptions/load-sample-prescriptions?user_id=${encodeURIComponent(targetUserId)}`, {
          method: 'POST'
        });
        if (fallbackRes.ok) {
          await loadPrescriptions();
          analysisApi.analyse(targetUserId).catch(() => {});
          return;
        }
      } catch (fallbackErr) {
        console.error('Proxy fallback failed:', fallbackErr);
      }
      const msg = err?.response?.data?.detail || err?.message || 'Failed to load sample prescriptions.';
      setError(`Notice: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  if (analyzing) {
    return (
      <div className="min-h-[75vh] flex items-center justify-center p-4">
        <AnalysisProgress onComplete={() => navigate('/analysis')} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Heading */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-teal-700">Prescription Ingestion</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-0.5">
            Upload Prescriptions
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Upload one or multiple prescriptions from different doctors in JPG, PNG, or PDF format.
          </p>
        </div>

        <button
          onClick={handleLoadSamples}
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-teal-50 hover:bg-teal-100 text-teal-800 border border-teal-200 font-bold text-xs transition shadow-xs"
        >
          <Sparkles className="w-4 h-4 text-teal-600" />
          <span>Load 3 Multi-Doctor Sample Prescriptions</span>
        </button>
      </div>

      <SafetyBanner compact />

      {error && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Drag and Drop Zone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-slate-300 hover:border-teal-500 bg-slate-50/60 hover:bg-teal-50/20 rounded-3xl p-8 sm:p-12 text-center cursor-pointer transition group"
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          multiple
          accept=".jpg,.jpeg,.png,.pdf"
          className="hidden"
        />
        <div className="w-16 h-16 rounded-2xl bg-white shadow-md text-teal-600 mx-auto flex items-center justify-center mb-4 group-hover:scale-105 transition">
          <Upload className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-bold text-slate-800">
          Click or drag & drop prescription files here
        </h3>
        <p className="text-xs text-slate-500 mt-1.5 max-w-sm mx-auto leading-relaxed">
          Supports multi-file uploads: JPG, JPEG, PNG photographs or scanned PDFs up to 25MB each.
        </p>
        <span className="inline-block mt-4 text-xs font-bold text-teal-700 bg-teal-50 px-3 py-1 rounded-full border border-teal-200">
          Select Multiple Files at Once
        </span>
      </div>

      {/* Staged New Files (Not yet uploaded) */}
      {selectedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-2">
            <Files className="w-4 h-4 text-teal-600" />
            <span>Files Ready to Process ({selectedFiles.length})</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {selectedFiles.map((file, idx) => (
              <div key={idx} className="bg-white p-3.5 rounded-xl border border-teal-300 shadow-xs flex items-center justify-between">
                <div className="overflow-hidden pr-2">
                  <p className="text-sm font-bold text-slate-900 truncate">{file.name}</p>
                  <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeSelectedFile(idx);
                  }}
                  className="text-slate-400 hover:text-rose-600 p-1"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Existing Prescriptions in Database */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 pb-2">
          <h3 className="text-base font-bold text-slate-900">
            Analyzed Prescriptions ({existingPrescriptions.length})
          </h3>
          <span className="text-xs text-slate-500">
            All documents included in safety cross-reference
          </span>
        </div>

        {existingPrescriptions.length === 0 && selectedFiles.length === 0 ? (
          <div className="text-center py-10 bg-white rounded-2xl border border-slate-200 text-slate-400 text-sm">
            <FileText className="w-10 h-10 mx-auto text-slate-300 mb-2" />
            <p>No prescriptions uploaded yet.</p>
            <p className="text-xs text-slate-400 mt-1">Upload photos/PDFs or load realistic sample prescriptions above.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {existingPrescriptions.map((rx) => (
              <PrescriptionCard
                key={rx.id}
                prescription={rx}
                onRemove={handleRemoveExisting}
              />
            ))}
          </div>
        )}
      </div>

      {/* Primary Analyse Button */}
      {(selectedFiles.length > 0 || existingPrescriptions.length > 0) && (
        <div className="pt-4 border-t border-slate-200 flex justify-end">
          <button
            onClick={handleUploadAndAnalyze}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-black text-base shadow-lg shadow-teal-600/25 transition flex items-center justify-center space-x-2.5"
          >
            <Sparkles className="w-5 h-5" />
            <span>Analyse Prescriptions</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
}
