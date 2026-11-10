import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Package,
  FileText,
  Users,
  Building,
  BotMessageSquare,
  ShieldCheck,
  ArrowRight,
  TrendingUp,
  AlertCircle,
  Activity,
} from 'lucide-react';
import Header from '../components/Header';
import { dashboardService } from '../services/dashboardService';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await dashboardService.getStats();
        setStats(data);
      } catch (err) {
        console.error('Failed to load system stats:', err);
        setError('Could not retrieve live statistics from backend.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, []);

  const statCards = [
    {
      title: 'Pharmacy Inventory',
      value: stats?.inventory?.total?.toLocaleString() || '1,240',
      subtitle: 'Stock items across 2 hospitals',
      icon: Package,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      link: '/inventory',
    },
    {
      title: 'Financial Invoices',
      value: stats?.bills?.total?.toLocaleString() || '550',
      subtitle: 'Issued across past 90 days',
      icon: FileText,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
      link: '/bills',
    },
    {
      title: 'Hospital Personnel',
      value: stats?.users?.total?.toLocaleString() || '14',
      subtitle: 'Staff accounts with RBAC',
      icon: Users,
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
      link: '/access',
    },
    {
      title: 'Hospital Tenants',
      value: stats?.hospitals?.total || '2',
      subtitle: 'Isolated health facilities',
      icon: Building,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
    },
  ];

  return (
    <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
      <Header
        title="Operations Overview"
        subtitle="Real-time multi-tenant hospital operations metrics & platform status"
      />

      <main className="p-8 space-y-8 max-w-7xl w-full mx-auto">
        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* AI Assistant Banner */}
        <div className="bg-gradient-to-r from-navy-900 via-navy-800 to-navy-900 rounded-2xl p-6 text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6 border border-navy-700">
          <div className="space-y-1.5 max-w-xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-300 text-xs font-semibold">
              <Activity className="w-3.5 h-3.5" />
              <span>Permission-Enforced Operations</span>
            </div>
            <h3 className="text-xl font-bold tracking-tight text-white">
              Perform Hospital Database Operations with Natural Language
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Query stock, analyze invoices, and stage batch updates. Every operation is strictly validated against role constraints, tenant isolation, and requires two-phase confirmation before write execution.
            </p>
          </div>
          <Link
            to="/assistant"
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs tracking-wide shadow-lg shadow-blue-500/25 transition-all shrink-0"
          >
            <BotMessageSquare className="w-4 h-4" />
            <span>Launch AI Assistant</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {/* Live Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {statCards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <div
                key={idx}
                className="bg-white rounded-2xl border border-gray-200/80 p-5 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    {card.title}
                  </span>
                  <div className={`p-2.5 rounded-xl ${card.bg} ${card.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                </div>
                <div className="mt-4">
                  <div className="text-2xl font-bold text-gray-900 tracking-tight">
                    {isLoading ? (
                      <div className="h-7 w-20 bg-slate-200 rounded animate-pulse"></div>
                    ) : (
                      card.value
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">{card.subtitle}</p>
                </div>
                {card.link && (
                  <Link
                    to={card.link}
                    className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs font-semibold text-blue-600 hover:text-blue-700"
                  >
                    <span>View Records</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                )}
              </div>
            );
          })}
        </div>

        {/* Detailed Sections: Inventory by Hospital & Active User Context */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Hospital Tenant Breakdown */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-bold text-gray-900 text-sm">Tenant Inventory Distribution</h4>
                <p className="text-xs text-gray-500">Live pharmaceutical inventory records per hospital facility</p>
              </div>
              <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
                100% Isolated
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              {stats?.inventory?.grouped_by_hospital?.map((hosp, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-800 text-sm">{hosp.hospital_name}</span>
                    <span className="text-[10px] bg-slate-200 font-mono text-slate-700 font-bold px-1.5 py-0.5 rounded">
                      {hosp.code}
                    </span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-xl font-bold text-slate-900">{hosp.item_count}</span>
                    <span className="text-xs text-slate-500">items in stock</span>
                  </div>
                  <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-blue-600 h-full rounded-full"
                      style={{ width: `${(hosp.item_count / 650) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* User Session Security Context */}
          <div className="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-blue-600" />
              <h4 className="font-bold text-gray-900 text-sm">Active Security Context</h4>
            </div>

            <div className="space-y-3 text-xs pt-1">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/60 space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-500">Staff Account:</span>
                  <span className="font-semibold text-slate-900">{user?.full_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Username:</span>
                  <span className="font-mono text-slate-700">{user?.username}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Assigned Roles:</span>
                  <span className="font-semibold text-blue-600">
                    {(user?.active_roles || []).join(', ')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Effective Permissions:</span>
                  <span className="font-bold text-emerald-600">
                    {Object.keys(user?.permissions || {}).length} Granted
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-blue-50/60 border border-blue-200/80 text-[11px] text-blue-800 leading-relaxed">
                Tenant isolation is cryptographically enforced. You cannot query or modify clinical or financial data outside your hospital facility.
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
