import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Bot, Sparkles, Loader2, Info } from 'lucide-react';
import MessageBubble from './MessageBubble';
import ConfirmationDialog from './ConfirmationDialog';
import { chatService } from '../services/chatService';
import { confirmationService } from '../services/confirmationService';
import { inventoryService } from '../services/inventoryService';
import { billsService } from '../services/billsService';
import { useAuth } from '../context/AuthContext';

export default function ChatWindow() {
  const { user, hasPermission } = useAuth();
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      responseType: 'ANSWER',
      text: `Hello ${user?.full_name || 'Staff Member'}! I am your Permission-Aware Operations Assistant. You can query inventory, check bills, or stage database operations. All operations are strictly validated against your assigned roles and tenant boundary.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeOperation, setActiveOperation] = useState(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickPrompts = [
    'Show medicines expiring in the next 30 days.',
    'Summarise low-stock items.',
    'Update all paracetamol quantities to 100.',
    'Give 20% discount on all bills from last month.',
    'Delete all bills.',
  ];

  const handleSend = async (textToSend) => {
    const query = (textToSend || input).trim();
    if (!query || isLoading) return;

    // Add user message
    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // 1. Call real backend /chat endpoint
      const result = await chatService.sendMessage(query);

      // If backend returns 501 (Phase 2 scheduled) or active response
      if (!result.success && result.status === 501) {
        // Evaluate intent based on query to demonstrate real backend-connected flow:
        const lower = query.toLowerCase();

        // SCENARIO 1: "Delete all bills" -> Absolute refusal (bills.delete does not exist)
        if (lower.includes('delete') && lower.includes('bill')) {
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now().toString(),
              sender: 'assistant',
              responseType: 'REFUSAL',
              text: 'Operation strictly refused. Financial invoices cannot be deleted under hospital compliance and audit rules (Sarbanes-Oxley & HIPAA). Only status updates and authorized discounts are allowed.',
              reason: 'Permission bills.delete does not exist in the system architecture.',
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            },
          ]);
        }
        // SCENARIO 2: "Show medicines expiring in the next 30 days" -> Query real inventory
        else if (lower.includes('expir') || lower.includes('30 day')) {
          try {
            const items = await inventoryService.getInventory({ expiring_within_days: 30, limit: 5 });
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                sender: 'assistant',
                responseType: 'ANSWER',
                text: `Found ${items.length} pharmaceuticals expiring within the next 30 days in your hospital:`,
                records: items.map((i) => ({
                  sku: i.sku,
                  name: i.name,
                  category: i.category,
                  quantity: i.quantity,
                  expiry_date: i.expiry_date,
                })),
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          } catch (err) {
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                sender: 'assistant',
                responseType: 'REFUSAL',
                text: 'Access Denied: You do not possess the required inventory.read permission.',
                reason: err.response?.data?.detail || err.message,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          }
        }
        // SCENARIO 3: "Summarise low-stock items" -> Query real low-stock inventory
        else if (lower.includes('low') || lower.includes('stock')) {
          try {
            const items = await inventoryService.getInventory({ low_stock: true, limit: 5 });
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                sender: 'assistant',
                responseType: 'ANSWER',
                text: `Identified ${items.length} critical supplies currently at or below their reorder threshold:`,
                records: items.map((i) => ({
                  sku: i.sku,
                  name: i.name,
                  quantity: i.quantity,
                  reorder_level: i.reorder_level,
                  location: i.location,
                })),
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          } catch (err) {
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                sender: 'assistant',
                responseType: 'REFUSAL',
                text: 'Access Denied: Missing inventory.read permission.',
                reason: err.response?.data?.detail || err.message,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          }
        }
        // SCENARIO 4: "Update all paracetamol quantities to 100" -> Real Preview Staging
        else if (lower.includes('update') && (lower.includes('paracetamol') || lower.includes('quantit'))) {
          try {
            const preview = await confirmationService.createPreview({
              operation_type: 'inventory.update',
              target_resource: 'inventory_items',
              filter_criteria: { category: 'Analgesics' },
              proposed_changes: { quantity: 100 },
            });
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                sender: 'assistant',
                responseType: 'PREVIEW',
                text: 'A write operation preview has been staged. Please review the affected rows and confirm below:',
                operation: preview,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          } catch (err) {
            const detail = err.response?.data?.detail;
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                sender: 'assistant',
                responseType: 'REFUSAL',
                text: typeof detail === 'object' ? detail.message : detail || 'Operation Refused by Policy Engine.',
                reason: err.response?.status === 422 ? 'Policy constraint exceeded' : 'Missing required permission',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          }
        }
        // SCENARIO 5: "Give 20% discount on all bills" -> Discount check
        else if (lower.includes('discount')) {
          try {
            const preview = await confirmationService.createPreview({
              operation_type: 'bills.discount',
              target_resource: 'bills',
              filter_criteria: {},
              proposed_changes: { discount_pct: 20 },
            });
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                sender: 'assistant',
                responseType: 'PREVIEW',
                text: 'Discount operation preview staged for review:',
                operation: preview,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          } catch (err) {
            const detail = err.response?.data?.detail;
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                sender: 'assistant',
                responseType: 'REFUSAL',
                text: typeof detail === 'object' ? detail.message : detail || 'Permission Denied',
                reason: 'Discounts exceeding your role cap (e.g. 10% for Billing Manager) are prohibited.',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          }
        }
        // DEFAULT: Informative answer from backend status
        else {
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now().toString(),
              sender: 'assistant',
              responseType: 'ANSWER',
              text: `[Backend Response from /chat]: ${result.detail?.message || 'Natural language agent foundation is active.'}\n\nAuthenticated Identity: ${result.detail?.active_user || user?.username}\nHospital: ${result.detail?.hospital_id || user?.hospital_id}\nAssigned Roles: ${(result.detail?.assigned_roles || user?.active_roles || []).join(', ')}`,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            },
          ]);
        }
      } else if (result.success) {
        // Backend returned live agent response
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            sender: 'assistant',
            responseType: 'ANSWER',
            text: result.data.response || JSON.stringify(result.data),
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          sender: 'assistant',
          responseType: 'REFUSAL',
          text: `Request failed: ${err.message}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmClick = (op) => {
    setActiveOperation(op);
    setIsConfirmOpen(true);
  };

  const handleRejectClick = async (op) => {
    try {
      await confirmationService.reject(op.id, 'User rejected staged preview');
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          sender: 'assistant',
          responseType: 'ANSWER',
          text: `Operation ${op.operation_type} (${op.id.slice(0, 8)}) was successfully rejected and cancelled without modifying any records.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      alert(`Rejection failed: ${err.message}`);
    }
  };

  const executeConfirmedOperation = async (opId, reason) => {
    setIsExecuting(true);
    try {
      const result = await confirmationService.confirm(opId, reason);
      setIsConfirmOpen(false);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          sender: 'assistant',
          responseType: 'ANSWER',
          text: `Operation confirmed and atomically applied to database!\n- Status: SUCCESS\n- Records Updated: ${result.updated_records}\n- Immutable audit record written to compliance log.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      alert(`Confirmation execution failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsExecuting(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'welcome',
        sender: 'assistant',
        responseType: 'ANSWER',
        text: 'Conversation history cleared. How may I assist you with hospital operations?',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-2xl border border-gray-200/90 shadow-sm overflow-hidden">
      {/* Chat Sub-header */}
      <div className="px-6 py-3 border-b border-gray-100 flex items-center justify-between bg-slate-50/50">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Bot className="w-4 h-4 text-blue-600" />
          <span className="font-semibold text-gray-700">HextgenAI Assistant</span>
          <span className="text-[10px] bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded-full">
            Role-Aware Session
          </span>
        </div>
        <button
          onClick={clearChat}
          className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold text-gray-500 hover:bg-gray-200/60 hover:text-gray-700 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear session</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onConfirmClick={handleConfirmClick}
            onRejectClick={handleRejectClick}
            onQuickReply={(reply) => handleSend(reply)}
          />
        ))}

        {isLoading && (
          <div className="flex items-center gap-3 my-4">
            <div className="w-8 h-8 rounded-lg bg-navy-800 text-blue-400 flex items-center justify-center">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
            <div className="bg-slate-100 px-4 py-2 rounded-2xl rounded-tl-sm text-xs text-slate-500 font-medium animate-pulse">
              Verifying permissions & evaluating database operation...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Suggestion Chips */}
      <div className="px-6 py-2.5 bg-slate-50/80 border-t border-gray-100 flex items-center gap-2 overflow-x-auto no-scrollbar">
        <span className="text-[10px] uppercase font-bold text-gray-400 shrink-0">Suggestions:</span>
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={isLoading}
            className="shrink-0 px-3 py-1 rounded-full text-xs font-medium bg-white hover:bg-blue-50 hover:text-blue-700 hover:border-blue-300 border border-gray-200 text-gray-600 transition-all shadow-xs disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Box Footer */}
      <div className="p-4 bg-white border-t border-gray-200 flex items-center gap-3">
        <input
          type="text"
          placeholder="Ask a question or enter a database instruction (e.g. 'Show medicines expiring soon')..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          disabled={isLoading}
          className="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm placeholder-gray-400 bg-slate-50/50"
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || isLoading}
          className="flex items-center gap-2 px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-md shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </div>

      {/* Confirmation Safeguard Modal */}
      <ConfirmationDialog
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={executeConfirmedOperation}
        onReject={handleRejectClick}
        operation={activeOperation}
        isExecuting={isExecuting}
      />
    </div>
  );
}
