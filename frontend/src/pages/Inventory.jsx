import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import DataTable from '../components/DataTable';
import { Search, Filter, AlertTriangle, Clock, ShieldAlert } from 'lucide-react';
import { inventoryService } from '../services/inventoryService';
import { useAuth } from '../context/AuthContext';

export default function Inventory() {
  const { hasPermission } = useAuth();
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters & Pagination state
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [lowStock, setLowStock] = useState(false);
  const [expiringSoon, setExpiringSoon] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 50;

  const canRead = hasPermission('inventory.read');

  useEffect(() => {
    if (!canRead) {
      setIsLoading(false);
      return;
    }

    const fetchInventory = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const params = {
          limit: pageSize,
          offset: (page - 1) * pageSize,
        };
        if (search.trim()) params.search = search.trim();
        if (category) params.category = category;
        if (lowStock) params.low_stock = true;
        if (expiringSoon) params.expiring_within_days = 30;

        const data = await inventoryService.getInventory(params);
        setItems(data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch inventory records.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchInventory();
  }, [page, category, lowStock, expiringSoon, search, canRead]);

  const columns = [
    {
      header: 'SKU / Code',
      accessor: 'sku',
      render: (row) => <span className="font-mono font-semibold text-slate-800">{row.sku}</span>,
    },
    {
      header: 'Pharmaceutical Name',
      accessor: 'name',
      render: (row) => (
        <div>
          <p className="font-semibold text-gray-900">{row.name}</p>
          <p className="text-[10px] text-gray-400 font-mono">Batch: {row.batch_number}</p>
        </div>
      ),
    },
    {
      header: 'Category',
      accessor: 'category',
      render: (row) => (
        <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-medium text-[11px]">
          {row.category}
        </span>
      ),
    },
    {
      header: 'Stock Qty',
      accessor: 'quantity',
      render: (row) => {
        const isLow = row.quantity <= row.reorder_level;
        return (
          <div className="flex items-center gap-1.5">
            <span className={`font-bold ${isLow ? 'text-rose-600' : 'text-slate-900'}`}>
              {row.quantity}
            </span>
            {isLow && (
              <span className="px-1.5 py-0.2 bg-rose-100 text-rose-700 rounded text-[10px] font-semibold">
                Low
              </span>
            )}
          </div>
        );
      },
    },
    {
      header: 'Reorder Lvl',
      accessor: 'reorder_level',
      render: (row) => <span className="text-gray-500">{row.reorder_level}</span>,
    },
    {
      header: 'Unit Price',
      accessor: 'unit_price',
      align: 'right',
      render: (row) => <span className="font-mono font-semibold">${Number(row.unit_price).toFixed(2)}</span>,
    },
    {
      header: 'Expiry Date',
      accessor: 'expiry_date',
      render: (row) => {
        const isExpiredOrClose =
          new Date(row.expiry_date) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
        return (
          <span
            className={`font-mono text-xs ${
              isExpiredOrClose ? 'text-amber-600 font-semibold' : 'text-slate-600'
            }`}
          >
            {row.expiry_date}
          </span>
        );
      },
    },
    {
      header: 'Location',
      accessor: 'location',
      render: (row) => <span className="text-gray-500 text-[11px]">{row.location || 'N/A'}</span>,
    },
  ];

  if (!canRead) {
    return (
      <div className="flex-1 flex flex-col min-w-0">
        <Header title="Pharmacy Inventory" subtitle="Stock inventory management" />
        <main className="p-8 max-w-4xl mx-auto flex-1 flex items-center justify-center">
          <div className="bg-white rounded-2xl border border-rose-200 p-8 text-center max-w-md shadow-sm space-y-3">
            <ShieldAlert className="w-12 h-12 text-rose-500 mx-auto" />
            <h3 className="font-bold text-gray-900 text-base">Access Restricted</h3>
            <p className="text-xs text-gray-500 leading-relaxed">
              Your assigned role does not hold the required <code className="bg-slate-100 px-1 py-0.5 rounded text-rose-600 font-mono">inventory.read</code> permission to view hospital pharmacy stock.
            </p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
      <Header
        title="Pharmacy Inventory"
        subtitle="Manage pharmaceutical stock, track batches, and monitor expiration dates"
      />

      <main className="p-8 space-y-6 max-w-7xl w-full mx-auto">
        {/* Filters Bar */}
        <div className="bg-white p-4 rounded-xl border border-gray-200/90 shadow-sm flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
            {/* Search Input */}
            <div className="relative min-w-[220px] flex-1">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search by name, SKU, or batch..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="w-full pl-9 pr-3 py-2 rounded-lg border border-gray-200 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50/50"
              />
            </div>

            {/* Category Dropdown */}
            <select
              value={category}
              onChange={(e) => {
                setCategory(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 rounded-lg border border-gray-200 text-xs bg-slate-50/50 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              <option value="Antibiotics">Antibiotics</option>
              <option value="Analgesics">Analgesics</option>
              <option value="Cardiology">Cardiology</option>
              <option value="Emergency">Emergency</option>
              <option value="Surgical Supplies">Surgical Supplies</option>
              <option value="Oncology">Oncology</option>
              <option value="Respiratory">Respiratory</option>
              <option value="Anesthesia">Anesthesia</option>
              <option value="IV Fluids">IV Fluids</option>
            </select>
          </div>

          {/* Quick Filters Toggles */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setLowStock(!lowStock);
                setPage(1);
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all ${
                lowStock
                  ? 'bg-rose-50 border-rose-300 text-rose-700'
                  : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
              <span>Low Stock Only</span>
            </button>

            <button
              onClick={() => {
                setExpiringSoon(!expiringSoon);
                setPage(1);
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all ${
                expiringSoon
                  ? 'bg-amber-50 border-amber-300 text-amber-800'
                  : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Clock className="w-3.5 h-3.5 text-amber-600" />
              <span>Expiring in 30 Days</span>
            </button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
            {error}
          </div>
        )}

        {/* Inventory Data Table */}
        <DataTable
          columns={columns}
          data={items}
          isLoading={isLoading}
          pagination={{ page, pageSize }}
          onPageChange={(newPage) => setPage(newPage)}
          emptyMessage="No inventory items match the selected filters."
        />
      </main>
    </div>
  );
}
