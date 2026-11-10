import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import DataTable from '../components/DataTable';
import { History, ShieldAlert, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import { auditService } from '../services/auditService';
import { useAuth } from '../context/AuthContext';

export default function AuditLogs() {
  const { hasPermission } = useAuth();
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const pageSize = 50;

  const canRead = hasPermission('audit.read');

  useEffect(() => {
    if (!canRead) {
      setIsLoading(false);
      return;
    }

    const fetchLogs = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const params = {
          limit: pageSize,
          offset: (page - 1) * pageSize,
        };
        const data = await auditService.getAuditLogs(params);
        setLogs(data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch compliance audit records.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchLogs();
  }, [page, canRead]);

  const getStatusBadge = (status) => {
    const s = (status || '').toUpperCase();
    if (s === 'SUCCESS') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-semibold">
          <CheckCircle2 className="w-3 h-3" />
          <span>Success</span>
        </span>
      );
    }
    if (s === 'DENIED') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px] font-semibold">
          <AlertTriangle className="w-3 h-3" />
          <span>Denied</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 text-[10px] font-semibold">
        <XCircle className="w-3 h-3" />
        <span>Failed</span>
      </span>
    );
  };

  const columns = [
    {
      header: 'Timestamp',
      accessor: 'created_at',
      render: (row) => (
        <span className="font-mono text-xs text-gray-500">
          {new Date(row.created_at).toLocaleString()}
        </span>
      ),
    },
    {
      header: 'Operation Action',
      accessor: 'action',
      render: (row) => (
        <span className="font-mono font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded text-xs border border-blue-200/60">
          {row.action}
        </span>
      ),
    },
    {
      header: 'Resource Target',
      accessor: 'resource_type',
      render: (row) => (
        <div>
          <span className="font-medium text-gray-800 capitalize">{row.resource_type}</span>
          {row.resource_id && (
            <p className="text-[10px] text-gray-400 font-mono">ID: {row.resource_id.slice(0, 10)}...</p>
          )}
        </div>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (row) => getStatusBadge(row.status),
    },
    {
      header: 'Client Details',
      accessor: 'ip_address',
      render: (row) => (
        <span className="text-gray-500 font-mono text-[11px]">{row.ip_address || 'Internal Service'}</span>
      ),
    },
    {
      header: 'Context / Metadata',
      accessor: 'metadata_info',
      render: (row) => (
        <span className="font-mono text-[10px] text-gray-500 truncate max-w-xs block">
          {JSON.stringify(row.metadata_info || {})}
        </span>
      ),
    },
  ];

  if (!canRead) {
    return (
      <div className="flex-1 flex flex-col min-w-0">
        <Header title="Compliance Audit Logs" subtitle="Tamper-proof compliance trail" />
        <main className="p-8 max-w-4xl mx-auto flex-1 flex items-center justify-center">
          <div className="bg-white rounded-2xl border border-rose-200 p-8 text-center max-w-md shadow-sm space-y-3">
            <ShieldAlert className="w-12 h-12 text-rose-500 mx-auto" />
            <h3 className="font-bold text-gray-900 text-base">Access Restricted</h3>
            <p className="text-xs text-gray-500 leading-relaxed">
              Your role does not possess the required <code className="bg-slate-100 px-1 py-0.5 rounded text-rose-600 font-mono">audit.read</code> permission to view hospital compliance audit logs. Only authorized Administrators can view audit entries.
            </p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
      <Header
        title="Compliance Audit Logs"
        subtitle="Immutable security audit trail capturing all database operations and authentication events"
      />

      <main className="p-8 space-y-6 max-w-7xl w-full mx-auto">
        {/* Info Banner */}
        <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-slate-700 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-blue-600" />
            <span>Audit log records are immutable and append-only. Modification or deletion is cryptographically prevented.</span>
          </div>
          <span className="text-[10px] font-mono uppercase bg-white border border-slate-300 px-2 py-0.5 rounded font-bold text-slate-600">
            Append-Only
          </span>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
            {error}
          </div>
        )}

        {/* Logs Table */}
        <DataTable
          columns={columns}
          data={logs}
          isLoading={isLoading}
          pagination={{ page, pageSize }}
          onPageChange={(newPage) => setPage(newPage)}
          emptyMessage="No audit logs recorded for this tenant yet."
        />
      </main>
    </div>
  );
}
