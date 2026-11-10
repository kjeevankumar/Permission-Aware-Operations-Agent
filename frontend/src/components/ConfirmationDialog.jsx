import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, XCircle, ShieldAlert, Loader2 } from 'lucide-react';

export default function ConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  onReject,
  operation,
  isExecuting = false,
}) {
  const [reason, setReason] = useState('');
  const [rowCountInput, setRowCountInput] = useState('');

  if (!isOpen || !operation) return null;

  const rowCount = operation.impacted_row_count || 0;
  const requiresExactCount = rowCount > 50;
  const isCountValid = !requiresExactCount || parseInt(rowCountInput, 10) === rowCount;

  const handleConfirm = () => {
    if (!isCountValid) return;
    onConfirm(operation.id, reason);
  };

  const handleReject = () => {
    onReject(operation.id, reason);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-2xl max-w-lg w-full shadow-2xl border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-50 border-b border-gray-200 flex items-center gap-3">
          <div className="p-2 rounded-lg bg-amber-100 text-amber-700">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900 text-base">
              Confirm Database Operation
            </h3>
            <p className="text-xs text-gray-500">
              Type: <span className="font-mono font-semibold text-blue-600">{operation.operation_type}</span>
            </p>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Target Resource:</span>
              <span className="font-semibold text-slate-800">{operation.target_resource}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Affected Records:</span>
              <span className="font-bold text-amber-600 text-sm">{rowCount} records</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Staged Expires In:</span>
              <span className="font-medium text-slate-700">
                {new Date(operation.expires_at).toLocaleTimeString()}
              </span>
            </div>
          </div>

          {/* Large Row Count Requirement */}
          {requiresExactCount && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-900 space-y-2">
              <div className="flex items-center gap-2 font-bold text-rose-700">
                <ShieldAlert className="w-4 h-4" />
                <span>Large Batch Operation Safeguard</span>
              </div>
              <p className="text-rose-800">
                This operation affects more than 50 rows ({rowCount} rows). To prevent accidental bulk mutations, please type the exact number of affected rows below:
              </p>
              <input
                type="number"
                placeholder={`Type ${rowCount} to confirm`}
                value={rowCountInput}
                onChange={(e) => setRowCountInput(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-rose-300 focus:outline-none focus:ring-2 focus:ring-rose-500 bg-white font-mono text-sm"
              />
            </div>
          )}

          {/* Audit Reason Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-700">
              Audit Justification / Reason (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g. Quarterly stock inventory calibration"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3.5 py-2 rounded-lg border border-gray-300 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="px-6 py-4 bg-slate-50 border-t border-gray-200 flex items-center justify-end gap-3">
          <button
            onClick={handleReject}
            disabled={isExecuting}
            className="px-4 py-2 rounded-lg border border-gray-300 text-xs font-semibold text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Reject Operation
          </button>
          <button
            onClick={handleConfirm}
            disabled={!isCountValid || isExecuting}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-md shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isExecuting ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Executing Atomic Write...</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-3.5 h-3.5" />
                <span>Confirm & Execute</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
