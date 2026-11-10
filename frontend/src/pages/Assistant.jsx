import React from 'react';
import Header from '../components/Header';
import ChatWindow from '../components/ChatWindow';
import { Shield, Sparkles, AlertTriangle, FileLock, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Assistant() {
  const { user } = useAuth();

  return (
    <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
      <Header
        title="AI Operations Assistant"
        subtitle="Role-aware database operations platform with staged previews and two-phase confirmation"
      />

      <main className="flex-1 p-6 max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6 overflow-hidden">
        {/* Main Chat Interface (Takes 3 columns) */}
        <div className="lg:col-span-3 flex flex-col min-h-0">
          <ChatWindow />
        </div>

        {/* Sidebar Info & Safety Guardrails (Takes 1 column) */}
        <div className="space-y-4 overflow-y-auto pr-1">
          {/* Active Role Status */}
          <div className="bg-white rounded-2xl border border-gray-200/80 p-5 shadow-sm space-y-3">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-blue-600" />
              <h4 className="font-bold text-gray-900 text-xs uppercase tracking-wider">
                Active Session Policies
              </h4>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center py-1 border-b border-gray-100">
                <span className="text-gray-500">Active Roles:</span>
                <span className="font-semibold text-blue-600">
                  {(user?.active_roles || []).join(', ')}
                </span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-gray-100">
                <span className="text-gray-500">Max Discount Limit:</span>
                <span className="font-semibold text-slate-800">
                  {user?.permissions?.['bills.discount']?.max_discount_pct !== undefined
                    ? `${user.permissions['bills.discount'].max_discount_pct}%`
                    : 'Not Allowed'}
                </span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-gray-100">
                <span className="text-gray-500">Max Rows Update:</span>
                <span className="font-semibold text-slate-800">
                  {user?.permissions?.['inventory.update']?.max_rows !== undefined
                    ? `${user.permissions['inventory.update'].max_rows} rows`
                    : 'Unlimited'}
                </span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-gray-500">Bill Visibility:</span>
                <span className="font-semibold text-slate-800">
                  {user?.permissions?.['bills.read']?.scope === 'own_records'
                    ? 'Own Records Only'
                    : 'Hospital Wide'}
                </span>
              </div>
            </div>
          </div>

          {/* Operational Guardrails Card */}
          <div className="bg-white rounded-2xl border border-gray-200/80 p-5 shadow-sm space-y-3 text-xs">
            <h4 className="font-bold text-gray-900 text-xs uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <span>Platform Safeguards</span>
            </h4>

            <ul className="space-y-2 text-gray-600 text-[11px] leading-relaxed">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                <span><strong>Two-Phase Protocol:</strong> Writes are dry-run previewed before confirmation.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                <span><strong>No Financial Deletions:</strong> Invoices cannot be erased; only status updates and discounts.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                <span><strong>Batch Protection:</strong> Bulk operations impacting &gt;50 rows require exact count confirmation.</span>
              </li>
              <li className="flex items-start gap-2">
                <FileLock className="w-3.5 h-3.5 text-blue-500 shrink-0 mt-0.5" />
                <span><strong>Prompt Injection Shield:</strong> Suspicious payload records cannot hijack authorization decisions.</span>
              </li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
