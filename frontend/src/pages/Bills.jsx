import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import DataTable from '../components/DataTable';
import { FileText, ShieldAlert, AlertCircle, Info } from 'lucide-react';
import { billsService } from '../services/billsService';
import { useAuth } from '../context/AuthContext';

export default function Bills() {
  const { user, hasPermission } = useAuth();
  const [bills, setBills] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 50;

  const canRead = hasPermission('bills.read');
  const isFrontDesk = user?.permissions?.['bills.read']?.scope === 'own_records';

  useEffect(() => {
    if (!canRead) {
      setIsLoading(false);
      return;
    }

    const fetchBills = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const params = {
          limit: pageSize,
          offset: (page - 1) * pageSize,
        };
        if (statusFilter) params.status = statusFilter;

        const data = await billsService.getBills(params);
        setBills(data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch billing invoices.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBills();
  }, [page, statusFilter, canRead]);

  const getStatusBadge = (status) => {
    const s = (status || '').toLowerCase();
    switch (s) {
      case 'paid':
        return <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold text-[10px]">Paid</span>;
      case 'pending':
        return <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold text-[10px]">Pending</span>;
      case 'draft':
        return <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-medium text-[10px]">Draft</span>;
      case 'cancelled':
        return <span className="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 font-semibold text-[10px]">Cancelled</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 font-medium text-[10px]">{status}</span>;
    }
  };

  const columns = [
    {
      header: 'Invoice #',
      accessor: 'bill_number',
      render: (row) => <span className="font-mono font-semibold text-slate-900">{row.bill_number}</span>,
    },
    {
      header: 'Patient Details',
      accessor: 'patient_name',
      render: (row) => (
        <div>
          <p className="font-semibold text-gray-900">{row.patient_name}</p>
          <p className="text-[10px] text-gray-400 font-mono">MRN: {row.patient_mrn}</p>
        </div>
      ),
    },
    {
      header: 'Bill Date',
      accessor: 'bill_date',
      render: (row) => (
        <span className="font-mono text-xs text-gray-500">
          {new Date(row.bill_date).toLocaleDateString()}
        </span>
      ),
    },
    {
      header: 'Gross Total',
      accessor: 'total_amount',
      align: 'right',
      render: (row) => <span className="font-mono">${Number(row.total_amount).toFixed(2)}</span>,
    },
    {
      header: 'Discount',
      accessor: 'discount_pct',
      align: 'right',
      render: (row) => {
        const disc = Number(row.discount_pct);
        return (
          <span className={`font-mono text-xs font-semibold ${disc > 0 ? 'text-amber-600' : 'text-gray-400'}`}>
            {disc > 0 ? `${disc.toFixed(1)}%` : '0%'}
          </span>
        );
      },
    },
    {
      header: 'Net Total',
      accessor: 'final_amount',
      align: 'right',
      render: (row) => (
        <span className="font-mono font-bold text-gray-900">
          ${Number(row.final_amount).toFixed(2)}
        </span>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (row) => getStatusBadge(row.status),
    },
  ];

  if (!canRead) {
    return (
      <div className="flex-1 flex flex-col min-w-0">
        <Header title="Hospital Billing" subtitle="Invoices & patient accounts" />
        <main className="p-8 max-w-4xl mx-auto flex-1 flex items-center justify-center">
          <div className="bg-white rounded-2xl border border-rose-200 p-8 text-center max-w-md shadow-sm space-y-3">
            <ShieldAlert className="w-12 h-12 text-rose-500 mx-auto" />
            <h3 className="font-bold text-gray-900 text-base">Access Restricted</h3>
            <p className="text-xs text-gray-500 leading-relaxed">
              Your role does not possess the required <code className="bg-slate-100 px-1 py-0.5 rounded text-rose-600 font-mono">bills.read</code> permission to inspect patient invoices.
            </p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
      <Header
        title="Hospital Billing & Invoices"
        subtitle="Manage patient statements, verify discounts, and check payment statuses"
      />

      <main className="p-8 space-y-6 max-w-7xl w-full mx-auto">
        {/* Scope Notice for Front Desk */}
        {isFrontDesk && (
          <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-center gap-3">
            <Info className="w-4 h-4 text-blue-600 shrink-0" />
            <span>
              <strong>Front Desk Scope Enforcement Active:</strong> You are viewing only patient bills initiated by your staff account (<code className="font-mono font-semibold">{user.username}</code>).
            </span>
          </div>
        )}

        {/* Filters Bar */}
        <div className="bg-white p-4 rounded-xl border border-gray-200/90 shadow-sm flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Status:</span>
            {['', 'paid', 'pending', 'draft', 'cancelled'].map((st) => (
              <button
                key={st}
                onClick={() => {
                  setStatusFilter(st);
                  setPage(1);
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
                  statusFilter === st
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-slate-50 border border-gray-200 text-gray-600 hover:bg-gray-100'
                }`}
              >
                {st || 'All Bills'}
              </button>
            ))}
          </div>

          <div className="text-[11px] text-gray-400 italic">
            * Deletions prohibited by financial audit regulations
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
            {error}
          </div>
        )}

        {/* Bills Data Table */}
        <DataTable
          columns={columns}
          data={bills}
          isLoading={isLoading}
          pagination={{ page, pageSize }}
          onPageChange={(newPage) => setPage(newPage)}
          emptyMessage="No billing records found matching criteria."
        />
      </main>
    </div>
  );
}
