import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, User, Eye, EyeOff, Loader2, ShieldCheck, AlertCircle, Building } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('admin.metro');
  const [password, setPassword] = useState('HospitalDemo2026!');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Invalid username or password. Please verify your credentials.');
      } else if (err.response?.status === 403) {
        setError('This user account is inactive or suspended.');
      } else {
        setError(err.response?.data?.detail || 'Unable to connect to authentication server.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const demoAccounts = [
    { label: 'Metro Admin', username: 'admin.metro', role: 'Admin (Full)' },
    { label: 'Metro Billing', username: 'billing.metro', role: 'Billing Mgr (10% max)' },
    { label: 'Metro Pharmacist', username: 'pharma.metro', role: 'Pharma (500 rows max)' },
    { label: 'Metro Front Desk', username: 'frontdesk.metro', role: 'Front Desk (Own records)' },
    { label: 'Metro Doctor', username: 'doctor.metro', role: 'Doctor (Clinical view)' },
    { label: 'St. Jude Admin', username: 'admin.jude', role: 'St. Jude Admin' },
    { label: 'St. Jude Billing', username: 'billing.jude', role: 'St. Jude Billing' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-navy-900 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-600 text-white font-black text-2xl shadow-xl shadow-blue-500/25 mb-4">
            H
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">
            Hextgen<span className="text-blue-400">AI</span>
          </h1>
          <p className="text-sm text-slate-400 font-medium mt-1">
            Permission-Aware Operations Agent
          </p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 p-8">
          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900">Hospital Staff Portal</h2>
            <p className="text-xs text-gray-500 mt-1">
              Sign in with your role-assigned credentials to continue.
            </p>
          </div>

          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username / Email Field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-700">Username / Staff ID</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  required
                  placeholder="e.g. admin.metro"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50/50"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-700">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50/50"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-lg shadow-blue-500/25 disabled:opacity-50 transition-all mt-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Sign In</span>
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Credentials Switcher */}
          <div className="mt-6 pt-5 border-t border-gray-100">
            <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2.5">
              Quick Test Accounts (Click to fill):
            </p>
            <div className="grid grid-cols-2 gap-1.5">
              {demoAccounts.map((acc) => (
                <button
                  key={acc.username}
                  type="button"
                  onClick={() => {
                    setUsername(acc.username);
                    setPassword('HospitalDemo2026!');
                  }}
                  className={`text-left p-2 rounded-lg border text-xs transition-all ${
                    username === acc.username
                      ? 'bg-blue-50 border-blue-300 text-blue-900 font-semibold'
                      : 'bg-slate-50 border-slate-200/80 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <p className="truncate font-semibold">{acc.label}</p>
                  <p className="text-[10px] text-slate-400 truncate">{acc.role}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Security Footer Note */}
        <p className="text-center text-xs text-slate-500 mt-6">
          Hospital-level tenant isolation & audit logging strictly active.
        </p>
      </div>
    </div>
  );
}
