import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import LanguageSelector from './LanguageSelector';
import { 
  ShieldCheck, 
  LayoutDashboard, 
  FileText, 
  Search, 
  Pill, 
  Bell, 
  History as HistoryIcon, 
  LogOut, 
  Menu, 
  X,
  LogIn
} from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { to: '/dashboard', label: t('nav.dashboard'), icon: LayoutDashboard },
    { to: '/prescriptions', label: t('nav.prescriptions'), icon: FileText },
    { to: '/analysis', label: t('nav.analysis'), icon: Search },
    { to: '/medications', label: t('nav.medications'), icon: Pill },
    { to: '/reminders', label: t('nav.reminders'), icon: Bell },
    { to: '/history', label: t('nav.history'), icon: HistoryIcon },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to={user ? '/dashboard' : '/'} className="flex items-center space-x-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-teal-600 flex items-center justify-center text-white shadow-md shadow-teal-500/20 group-hover:bg-teal-700 transition">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-black tracking-tight text-slate-900 leading-none">
                MediGuard <span className="text-teal-600 font-bold">AI</span>
              </span>
              <span className="text-[10px] text-slate-500 font-medium tracking-wide uppercase">
                Prescription Safety
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          {user ? (
            <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
              {navLinks.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.to || (item.to !== '/dashboard' && location.pathname.startsWith(item.to));
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-semibold transition ${
                      isActive
                        ? 'bg-teal-50 text-teal-700 shadow-sm border border-teal-200/60'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-teal-600' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          ) : (
            <nav className="hidden md:flex items-center space-x-6 text-sm font-medium text-slate-600">
              <a href="#features" className="hover:text-teal-600 transition">{t('nav.features')}</a>
              <a href="#how-it-works" className="hover:text-teal-600 transition">{t('nav.how_it_works')}</a>
              <a href="#safety" className="hover:text-teal-600 transition">{t('nav.safety')}</a>
            </nav>
          )}

          {/* Right Header Elements: Language Selector & User/Logout (NO Profile!) */}
          <div className="hidden md:flex items-center space-x-3">
            <LanguageSelector />

            {user ? (
              <div className="flex items-center space-x-3 pl-2 border-l border-slate-200">
                <div className="flex items-center space-x-2">
                  {user.avatar ? (
                    <img src={user.avatar} alt={user.name} className="w-8 h-8 rounded-full border border-slate-200 object-cover" />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-800 font-bold text-xs flex items-center justify-center border border-teal-200">
                      {user.name ? user.name.charAt(0).toUpperCase() : 'P'}
                    </div>
                  )}
                  <span className="text-sm font-medium text-slate-700 hidden lg:inline max-w-[120px] truncate">
                    {user.name}
                  </span>
                </div>

                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 transition border border-transparent hover:border-rose-100"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden lg:inline">{t('nav.logout')}</span>
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-semibold text-sm shadow-sm transition"
              >
                <LogIn className="w-4 h-4" />
                <span>{t('nav.login')}</span>
              </Link>
            )}
          </div>

          {/* Mobile Menu Trigger */}
          <div className="flex items-center space-x-2 md:hidden">
            <LanguageSelector />
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:bg-slate-100 focus:outline-none"
              aria-label="Open mobile menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-3 pb-5 space-y-2 shadow-lg">
          {user ? (
            <>
              <div className="pb-3 mb-2 border-b border-slate-100 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-800 font-bold text-xs flex items-center justify-center">
                    {user.name ? user.name.charAt(0).toUpperCase() : 'P'}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-slate-900">{user.name}</div>
                    <div className="text-xs text-slate-500">{user.email}</div>
                  </div>
                </div>
              </div>

              {navLinks.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.to;
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-semibold ${
                      isActive ? 'bg-teal-50 text-teal-700' : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <Icon className="w-4 h-4 text-teal-600" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}

              <div className="pt-2 border-t border-slate-100">
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleLogout();
                  }}
                  className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-semibold text-rose-600 hover:bg-rose-50"
                >
                  <LogOut className="w-4 h-4" />
                  <span>{t('nav.logout')}</span>
                </button>
              </div>
            </>
          ) : (
            <div className="space-y-2">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg bg-teal-600 text-white font-semibold text-sm"
              >
                <LogIn className="w-4 h-4" />
                <span>{t('nav.login')}</span>
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
