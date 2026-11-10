import React from 'react';
import { Shield, Building, UserCircle, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Header({ title, subtitle }) {
  const { user } = useAuth();

  const hospitalName = user?.username?.includes('metro')
    ? 'Metro Health General Hospital'
    : user?.username?.includes('jude')
    ? 'St. Jude Memorial Hospital'
    : 'Hospital Tenant Operations';

  return (
    <header className="h-16 bg-white border-b border-gray-200 px-8 flex items-center justify-between shrink-0 shadow-sm">
      {/* Title & Subtitle */}
      <div>
        <h2 className="text-lg font-bold text-gray-900 leading-tight">
          {title}
        </h2>
        {subtitle && (
          <p className="text-xs text-gray-500 font-normal">
            {subtitle}
          </p>
        )}
      </div>

      {/* Security & User Context Status Badges */}
      <div className="flex items-center gap-4">
        {/* Hospital Indicator */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200 text-xs font-medium text-slate-700">
          <Building className="w-3.5 h-3.5 text-blue-600" />
          <span className="font-semibold text-gray-900">{hospitalName}</span>
        </div>

        {/* Roles Badges */}
        <div className="flex items-center gap-1.5">
          {user?.active_roles?.map((role) => (
            <span
              key={role}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-blue-50 border border-blue-200/80 text-blue-700 font-semibold text-xs"
            >
              <Shield className="w-3 h-3 text-blue-600" />
              {role}
            </span>
          ))}
        </div>

        {/* Account Status Pill */}
        <div className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-700 font-medium text-xs">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          <span className="capitalize">{user?.account_status || 'Active'}</span>
        </div>
      </div>
    </header>
  );
}
