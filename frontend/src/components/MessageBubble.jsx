import React from 'react';
import { Bot, User, ShieldAlert, CheckCircle2, HelpCircle, FileDiff } from 'lucide-react';
import PreviewCard from './PreviewCard';

export default function MessageBubble({ message, onConfirmClick, onRejectClick, onQuickReply }) {
  const isUser = message.sender === 'user';
  const type = message.responseType || 'ANSWER';

  return (
    <div className={`flex gap-3 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-lg bg-navy-800 text-blue-400 border border-navy-700 flex items-center justify-center shrink-0 shadow-sm mt-0.5">
          <Bot className="w-4 h-4" />
        </div>
      )}

      <div className={`max-w-2xl flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Timestamp */}
        <span className="text-[10px] text-gray-400 mb-1 px-1">
          {message.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>

        {/* Message Bubble Body */}
        {isUser ? (
          <div className="bg-blue-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm shadow-sm text-sm">
            <p className="whitespace-pre-wrap">{message.text}</p>
          </div>
        ) : (
          <div className="bg-white border border-gray-200/90 rounded-2xl rounded-tl-sm p-4 shadow-sm text-sm text-gray-800 w-full space-y-3">
            {/* TYPE A: ANSWER */}
            {type === 'ANSWER' && (
              <div className="space-y-2">
                <div className="flex items-center gap-1.5 text-xs text-blue-600 font-semibold uppercase tracking-wider">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Agent Answer</span>
                </div>
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{message.text}</p>
                {/* Structured records table if present */}
                {message.records && message.records.length > 0 && (
                  <div className="mt-2 border border-gray-200 rounded-lg overflow-x-auto text-xs">
                    <table className="w-full text-left">
                      <thead className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold">
                        <tr>
                          {Object.keys(message.records[0]).slice(0, 5).map((key) => (
                            <th key={key} className="px-3 py-2 capitalize">{key.replace('_', ' ')}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {message.records.slice(0, 5).map((row, rIdx) => (
                          <tr key={rIdx} className="hover:bg-gray-50/50">
                            {Object.values(row).slice(0, 5).map((val, vIdx) => (
                              <td key={vIdx} className="px-3 py-2 text-gray-700">{String(val)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* TYPE B: CLARIFICATION */}
            {type === 'CLARIFICATION' && (
              <div className="space-y-3 bg-amber-50/60 p-3 rounded-xl border border-amber-200/70">
                <div className="flex items-center gap-1.5 text-xs text-amber-700 font-bold uppercase tracking-wider">
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>Clarification Required</span>
                </div>
                <p className="text-gray-800">{message.text}</p>
                {message.quickReplies && (
                  <div className="flex flex-wrap gap-2 pt-1">
                    {message.quickReplies.map((reply, idx) => (
                      <button
                        key={idx}
                        onClick={() => onQuickReply && onQuickReply(reply)}
                        className="px-3 py-1 rounded-full text-xs font-semibold bg-white border border-amber-300 text-amber-800 hover:bg-amber-100 transition-colors shadow-xs"
                      >
                        {reply}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* TYPE C: REFUSAL */}
            {type === 'REFUSAL' && (
              <div className="space-y-2 bg-rose-50/80 p-3.5 rounded-xl border border-rose-200">
                <div className="flex items-center gap-1.5 text-xs text-rose-700 font-bold uppercase tracking-wider">
                  <ShieldAlert className="w-4 h-4 text-rose-600" />
                  <span>Access Denied / Policy Violation</span>
                </div>
                <p className="text-sm font-medium text-rose-900">{message.text}</p>
                {message.reason && (
                  <p className="text-xs text-rose-700 mt-1 italic">
                    Reason: {message.reason}
                  </p>
                )}
              </div>
            )}

            {/* TYPE D: PREVIEW */}
            {type === 'PREVIEW' && (
              <div className="space-y-2">
                <div className="flex items-center gap-1.5 text-xs text-blue-700 font-bold uppercase tracking-wider">
                  <FileDiff className="w-4 h-4 text-blue-600" />
                  <span>Operation Staging Diff</span>
                </div>
                <p className="text-gray-700">{message.text}</p>
                {message.operation && (
                  <PreviewCard
                    operation={message.operation}
                    onConfirmClick={onConfirmClick}
                    onRejectClick={onRejectClick}
                  />
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}
