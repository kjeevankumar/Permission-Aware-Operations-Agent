import React from 'react';
import Header from '../components/Header';
import { Shield, Key, Lock, CheckCircle, Sliders, Users, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function UserAccess() {
  const { user } = useAuth();
  const permissions = user?.permissions || {};

  return (
    <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
      <Header
        title="Role & Permission Access Control"
        subtitle="Active user permissions, operational constraints, and individual overrides"
      />

      <main className="p-8 space-y-6 max-w-7xl w-full mx-auto">
        {/* User Identity Overview Card */}
        <div className="bg-white rounded-2xl border border-gray-200/90 p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center font-bold text-lg uppercase shadow-sm">
              {user?.full_name ? user.full_name.charAt(0) : 'U'}
            </div>
            <div>
              <h3 className="font-bold text-gray-900 text-base leading-tight">
                {user?.full_name}
              </h3>
              <p className="text-xs text-gray-500 font-mono mt-0.5">{user?.email}</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="px-3.5 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700">
              <span className="text-slate-400 mr-1.5">User ID:</span>
              <span className="font-mono font-semibold">{user?.user_id?.slice(0, 12)}...</span>
            </div>
            <div className="px-3.5 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700">
              <span className="text-slate-400 mr-1.5">Hospital ID:</span>
              <span className="font-mono font-semibold">{user?.hospital_id?.slice(0, 12)}...</span>
            </div>
          </div>
        </div>

        {/* Permissions & Dynamic Constraints Table */}
        <div className="bg-white rounded-2xl border border-gray-200/90 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-blue-600" />
              <h4 className="font-bold text-gray-900 text-sm">Effective Permissions Catalog</h4>
            </div>
            <span className="text-xs font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-md">
              {Object.keys(permissions).length} Capabilities Granted
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50/80 border-b border-gray-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="px-6 py-3">Permission Code</th>
                  <th className="px-6 py-3">Functional Scope</th>
                  <th className="px-6 py-3">Applied JSON Constraints</th>
                  <th className="px-6 py-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {Object.entries(permissions).map(([code, constraints]) => {
                  const hasConstraints = Object.keys(constraints).length > 0;
                  return (
                    <tr key={code} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-6 py-3.5 font-mono font-semibold text-blue-700">
                        {code}
                      </td>
                      <td className="px-6 py-3.5 text-gray-700 font-medium capitalize">
                        {code.split('.').join(' ')}
                      </td>
                      <td className="px-6 py-3.5">
                        {hasConstraints ? (
                          <span className="inline-flex items-center gap-1.5 font-mono text-[11px] bg-amber-50 text-amber-800 border border-amber-200 px-2.5 py-1 rounded-md font-semibold">
                            <Sliders className="w-3 h-3 text-amber-600" />
                            {JSON.stringify(constraints)}
                          </span>
                        ) : (
                          <span className="text-gray-400 italic">Unconstrained</span>
                        )}
                      </td>
                      <td className="px-6 py-3.5 text-right">
                        <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded text-[11px] font-semibold">
                          <CheckCircle className="w-3 h-3" />
                          <span>Active</span>
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Explanatory Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-2 text-xs">
            <h5 className="font-bold text-gray-900 flex items-center gap-2">
              <Shield className="w-4 h-4 text-blue-600" />
              <span>User Permission Overrides (`user_permission_overrides`)</span>
            </h5>
            <p className="text-gray-600 leading-relaxed text-[11px]">
              Individual staff accounts can have specific permissions granted or revoked directly without modifying the shared role for all other users. For example, an individual pharmacist can be temporarily suspended from updates while other pharmacists retain editing access.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-2 text-xs">
            <h5 className="font-bold text-gray-900 flex items-center gap-2">
              <Lock className="w-4 h-4 text-blue-600" />
              <span>Multi-Tenant Role Safety</span>
            </h5>
            <p className="text-gray-600 leading-relaxed text-[11px]">
              Roles and permissions are resolved exclusively on the server from the cryptographically verified JWT token and database records. The client cannot send or alter role or hospital parameters.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
