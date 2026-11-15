import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import SafetyBanner from '../components/SafetyBanner';
import { 
  ShieldCheck, 
  Upload, 
  Sparkles, 
  AlertTriangle, 
  Layers, 
  Gauge, 
  Globe2, 
  Volume2, 
  Bell, 
  FileText, 
  ArrowRight,
  CheckCircle2,
  Users
} from 'lucide-react';

export default function Landing() {
  const { user, loginWithGoogle, loginWithDemo } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleStart = () => {
    if (user) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  const features = [
    {
      icon: Upload,
      title: "Multiple Prescription Upload",
      desc: "Upload simultaneous prescriptions from different cardiologists, GPs, or surgeons in JPG, PNG, or PDF formats."
    },
    {
      icon: Sparkles,
      title: "AI Prescription Analysis",
      desc: "Extracts medicine names, strengths, dosages, frequencies, and durations using structured Gemini AI."
    },
    {
      icon: Layers,
      title: "Duplicate Medicine Detection",
      desc: "Instantly catches the exact same medicine or active ingredient prescribed under different brand names."
    },
    {
      icon: AlertTriangle,
      title: "Drug Interaction Detection",
      desc: "Verifies every pairwise combination against a trusted clinical drug database, categorized from LOW to CRITICAL."
    },
    {
      icon: Gauge,
      title: "Dosage Concern Detection",
      desc: "Calculates cumulative daily exposure across all doctors and warns if maximum safe therapeutic limits are exceeded."
    },
    {
      icon: ShieldCheck,
      title: "Medication Overlap Detection",
      desc: "Identifies therapeutic redundancies, such as taking multiple NSAIDs or duplicate acid reducers."
    },
    {
      icon: Globe2,
      title: "8 Regional Languages",
      desc: "Seamless translation across English, Tamil, Telugu, Hindi, Malayalam, Kannada, Bengali, and Marathi."
    },
    {
      icon: Volume2,
      title: "Voice Explanations",
      desc: "Listen to patient-friendly explanations in your native language with clear, spoken audio playback."
    },
    {
      icon: Bell,
      title: "Medication Reminders",
      desc: "Personalized morning, afternoon, evening, and night schedules with one-tap 'Mark as Taken' adherence logs."
    },
    {
      icon: FileText,
      title: "Consolidated Medication Summary",
      desc: "Synthesizes all approved prescriptions into one unified medication review plan ready to discuss with your doctor."
    },
    {
      icon: FileText,
      title: "Professional PDF Generation",
      desc: "Download an organized, doctor-ready PDF summary with warnings, prescription sources, and schedules."
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50 text-slate-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto space-y-6">
            <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-teal-50 border border-teal-200/80 text-teal-800 text-xs font-bold uppercase tracking-wider shadow-xs animate-in fade-in duration-300">
              <ShieldCheck className="w-4 h-4 text-teal-600" />
              <span>AI-Powered Prescription Safety Assistant</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-slate-900 tracking-tight leading-[1.1]">
              Your Prescriptions. <br />
              <span className="text-teal-600">One Safer Medication Plan.</span>
            </h1>

            <p className="text-lg sm:text-xl text-slate-600 leading-relaxed font-normal">
              {t('hero.subheading')}
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 pt-4">
              <button
                onClick={handleStart}
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-base shadow-lg shadow-teal-600/25 transition-all flex items-center justify-center space-x-2"
              >
                <span>{user ? "Go to Dashboard" : t('hero.cta_google')}</span>
                <ArrowRight className="w-5 h-5" />
              </button>

              {!user && (
                <button
                  onClick={async () => {
                    await loginWithDemo();
                    navigate('/dashboard');
                  }}
                  className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-white hover:bg-slate-100 text-slate-800 font-bold text-base border border-slate-300 transition-all shadow-sm flex items-center justify-center space-x-2"
                >
                  <Users className="w-5 h-5 text-teal-600" />
                  <span>{t('hero.demo_login')}</span>
                </button>
              )}
            </div>

            {/* Quick trust metrics */}
            <div className="pt-8 grid grid-cols-3 gap-4 border-t border-slate-200/70 max-w-lg mx-auto text-center">
              <div>
                <div className="text-2xl font-black text-slate-900">100%</div>
                <div className="text-xs text-slate-500 font-medium">Verified Drug Data</div>
              </div>
              <div>
                <div className="text-2xl font-black text-slate-900">8</div>
                <div className="text-xs text-slate-500 font-medium">Regional Languages</div>
              </div>
              <div>
                <div className="text-2xl font-black text-slate-900">0</div>
                <div className="text-xs text-slate-500 font-medium">AI Prescriptions</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mandatory Safety Notice Section */}
      <section id="safety" className="max-w-5xl mx-auto px-4 sm:px-6 mb-16">
        <SafetyBanner />
      </section>

      {/* How It Works Flow */}
      <section id="how-it-works" className="py-16 bg-slate-100/70 border-y border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-wider text-teal-700">Simple 4-Step Process</span>
            <h2 className="text-3xl font-black text-slate-900 mt-1">How MediGuard AI Protects You</h2>
            <p className="text-slate-600 text-sm mt-2">Designed to be effortlessly simple for elderly patients and busy caregivers.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { step: "01", title: "Upload Prescriptions", desc: "Snap photos or upload PDF prescriptions from all your different consulting doctors." },
              { step: "02", title: "Automated OCR & Extraction", desc: "MediGuard reads doctor notes, drug names, dosage strengths, and frequencies." },
              { step: "03", title: "Clinical Safety Check", desc: "Cross-references verified pharmacology databases for duplicates, overlaps, and interactions." },
              { step: "04", title: "Consolidated Plan & PDF", desc: "Review warnings with voice explanations, set reminders, and export a doctor-ready summary." }
            ].map((s) => (
              <div key={s.step} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm relative">
                <span className="text-4xl font-black text-teal-100 absolute top-4 right-4">{s.step}</span>
                <h3 className="text-base font-bold text-slate-900 mb-2 relative z-10">{s.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed relative z-10">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-teal-700">Comprehensive Capabilities</span>
            <h2 className="text-3xl sm:text-4xl font-black text-slate-900 mt-1">
              Engineered for Complete Patient Safety
            </h2>
            <p className="text-slate-600 text-base mt-2">
              Combining trusted pharmacology knowledge bases with intelligent Google Gemini explanations.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => {
              const Icon = f.icon;
              return (
                <div
                  key={f.title}
                  className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs hover:shadow-md hover:border-teal-200 transition group"
                >
                  <div className="w-12 h-12 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center mb-4 group-hover:bg-teal-600 group-hover:text-white transition">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">{f.title}</h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="bg-gradient-to-r from-teal-700 to-teal-900 text-white py-16">
        <div className="max-w-5xl mx-auto px-4 text-center space-y-6">
          <h2 className="text-3xl sm:text-4xl font-black">
            Never Risk Unintended Medication Overlaps Again
          </h2>
          <p className="text-teal-100 max-w-2xl mx-auto text-base">
            Upload your prescriptions in seconds and gain total clarity over your daily medication routine.
          </p>
          <button
            onClick={handleStart}
            className="px-8 py-3.5 rounded-xl bg-white text-teal-900 font-bold text-base shadow-xl hover:bg-teal-50 transition inline-flex items-center space-x-2"
          >
            <span>Get Started with MediGuard AI</span>
            <ArrowRight className="w-5 h-5 text-teal-800" />
          </button>
        </div>
      </section>
    </div>
  );
}
