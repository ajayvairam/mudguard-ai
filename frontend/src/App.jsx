import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import Navbar from './components/Navbar';

import Landing from './pages/Landing';
import Login from './pages/Login';
import AuthCallback from './pages/AuthCallback';
import Dashboard from './pages/Dashboard';
import UploadPrescription from './pages/UploadPrescription';
import Analysis from './pages/Analysis';
import MedicationPlan from './pages/MedicationPlan';
import Reminders from './pages/Reminders';
import History from './pages/History';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-10 h-10 border-4 border-teal-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <Router>
          <div className="min-h-screen flex flex-col bg-slate-50 font-sans antialiased text-slate-900 selection:bg-teal-100 selection:text-teal-900">
            <Navbar />
            <main className="flex-grow">
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<Landing />} />
                <Route path="/login" element={<Login />} />
                <Route path="/auth/callback" element={<AuthCallback />} />

                {/* Authenticated Application Routes (NO PROFILE PAGE!) */}
                <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                <Route path="/prescriptions" element={<ProtectedRoute><UploadPrescription /></ProtectedRoute>} />
                <Route path="/analysis" element={<ProtectedRoute><Analysis /></ProtectedRoute>} />
                <Route path="/medications" element={<ProtectedRoute><MedicationPlan /></ProtectedRoute>} />
                <Route path="/reminders" element={<ProtectedRoute><Reminders /></ProtectedRoute>} />
                <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>

            {/* Footer */}
            <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
                <div>
                  © 2026 <strong>MediGuard AI</strong> — Medication Safety & Multi-Prescription Analysis.
                </div>
                <div className="text-[11px] text-slate-600">
                  Medication safety assistance system • Not an autonomous prescriber
                </div>
              </div>
            </footer>
          </div>
        </Router>
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;
