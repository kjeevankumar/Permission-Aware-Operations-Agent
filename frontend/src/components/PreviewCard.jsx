import React from 'react';
import { Eye, ArrowRight, ShieldCheck, Clock, Check, X } from 'lucide-react';

export default function PreviewCard({ operation, onConfirmClick, onRejectClick }) {
  if (!operation) return null;

  const diffItems = operation.preview_diff?.diff || [];
  const rowCount = operation.impacted_row_count || 0;

  return (
    <div className="bg-white rounded-xl border border-blue-200 shadow-sm overflow-hidden my-3">
      {/* Header Banner */}
      <div className="bg-blue-50/80 px-4 py-3 border-b border-blue-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4 text-blue-600" />
          <span className="text-xs font-bold uppercase tracking-wider text-blue-900">
            Operation Preview Staged
          </span>
          <span className="text-[10px] bg-blue-100 text-blue-700 font-mono px-2 py-0.5 rounded-full font-semibold">
            {operation.operation_type}
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="font-semibold text-gray-700">Affected:</span>
          <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold">
            {rowCount} records
          </span>
        </div>
      </div>

      {/* Before / After Diff Samples */}
      <div className="p-4 space-y-3">
        <p className="text-xs font-semibold text-gray-600">Sample Proposed Changes Diff:</p>
        <div className="border border-gray-200 rounded-lg overflow-hidden text-xs">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-gray-500 font-medium">
                <th className="px-3 py-2">Target ID</th>
                <th className="px-3 py-2">Current State (Before)</th>
                <th className="px-3 py-2">Proposed State (After)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {diffItems.slice(0, 3).map((item, idx) => (
                <tr key={idx} className="hover:bg-gray-50/50">
                  <td className="px-3 py-2 font-mono text-gray-400 text-[10px]">
                    {item.id ? `${item.id.slice(0, 8)}...` : `#${idx + 1}`}
                  </td>
                  <td className="px-3 py-2 text-rose-700 bg-rose-50/30">
                    <pre className="font-mono text-[11px] whitespace-pre-wrap">
                      {JSON.stringify(item.before, null, 1)}
                    </pre>
                  </td>
                  <td className="px-3 py-2 text-emerald-700 bg-emerald-50/30">
                    <pre className="font-mono text-[11px] whitespace-pre-wrap">
                      {JSON.stringify(item.after, null, 1)}
                    </pre>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {diffItems.length > 3 && (
            <div className="px-3 py-1.5 bg-gray-50 border-t border-gray-200 text-center text-[10px] text-gray-500">
              + {diffItems.length - 3} more records staged in this batch
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div className="pt-2 flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <Clock className="w-3.5 h-3.5 text-gray-400" />
            <span>Expires at {new Date(operation.expires_at).toLocaleTimeString()}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onRejectClick(operation)}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-300 hover:bg-gray-100 text-gray-700 text-xs font-semibold transition-colors"
            >
              <X className="w-3.5 h-3.5 text-red-500" />
              <span>Cancel</span>
            </button>
            <button
              onClick={() => onConfirmClick(operation)}
              className="flex items-center gap-1 px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-all"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Review & Confirm</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
