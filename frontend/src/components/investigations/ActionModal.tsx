import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, XCircle, RotateCcw, Send, AlertTriangle } from 'lucide-react';
import type { ActionRecommendation, InvestigationState, DecisionFeedback } from '../../types';

interface ActionControlsProps {
  investigationId?: string;
  recommendation: ActionRecommendation | null | undefined;
  currentState: InvestigationState;
  onApprove: (notes?: string) => Promise<void>;
  onReject: (justification: string) => Promise<void>;
  onRollback: (rollback_reason: string) => Promise<void>;
  onRecordDecision: (decision: DecisionFeedback, justification: string) => Promise<void>;
  isLoading: boolean;
}

export const ActionControls: React.FC<ActionControlsProps> = ({
  recommendation,
  currentState,
  onApprove,
  onReject,
  onRollback,
  onRecordDecision,
  isLoading,
}) => {
  const [modalType, setModalType] = useState<'reject' | 'rollback' | 'decision' | null>(null);
  const [justification, setJustification] = useState('');
  const [selectedDecision, setSelectedDecision] = useState<DecisionFeedback>('CONFIRMED_FRAUD');

  const handleSubmit = async () => {
    if (!justification.trim()) return;

    if (modalType === 'reject') {
      await onReject(justification);
    } else if (modalType === 'rollback') {
      await onRollback(justification);
    } else if (modalType === 'decision') {
      await onRecordDecision(selectedDecision, justification);
    }
    setModalType(null);
    setJustification('');
  };

  const getActionColor = (action?: string) => {
    if (action === 'URGENT_SETTLEMENT_FREEZE') return 'text-red-400 bg-red-950/40 border-red-800/60';
    if (action === 'SETTLEMENT_REVIEW') return 'text-orange-400 bg-orange-950/40 border-orange-800/60';
    if (action === 'ENHANCED_MONITORING') return 'text-amber-400 bg-amber-950/40 border-amber-800/60';
    return 'text-emerald-400 bg-emerald-950/40 border-emerald-800/60';
  };

  return (
    <div className="p-5 rounded-xl border border-surface-border bg-surface-200/90 space-y-4">
      <div className="flex items-center justify-between border-b border-surface-border/70 pb-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-cyan-400" />
          <h4 className="text-sm font-bold text-slate-100">Bounded Action Recommendation & Decision</h4>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-300 border border-surface-border text-slate-400">
          Human-in-the-Loop Required
        </span>
      </div>

      {recommendation && (
        <div className="p-3.5 rounded-lg bg-surface-300/80 border border-surface-border space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">System Proposed Action:</span>
            <span className={`text-xs font-mono font-bold px-2.5 py-1 rounded border ${getActionColor(recommendation.action)}`}>
              {recommendation.action.replace(/_/g, ' ')}
            </span>
          </div>
          <p className="text-xs text-slate-300">{recommendation.reason}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center gap-3 pt-2">
        {currentState !== 'ACTIONED' && (
          <button
            onClick={() => onApprove('Analyst verified evidence and confirmed bounded risk action.')}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-semibold shadow-md transition-colors disabled:opacity-50"
          >
            <CheckCircle className="h-4 w-4" />
            <span>Approve Action</span>
          </button>
        )}

        {currentState !== 'CLEARED' && currentState !== 'CLOSED' && (
          <button
            onClick={() => setModalType('reject')}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-surface-50 hover:bg-surface-borderLight border border-surface-border text-slate-300 hover:text-white text-xs font-semibold transition-colors disabled:opacity-50"
          >
            <XCircle className="h-4 w-4 text-amber-400" />
            <span>Reject / Dismiss</span>
          </button>
        )}

        {currentState === 'ACTIONED' && (
          <button
            onClick={() => setModalType('rollback')}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-md transition-colors disabled:opacity-50"
          >
            <RotateCcw className="h-4 w-4" />
            <span>Rollback Action (Reversible)</span>
          </button>
        )}

        <button
          onClick={() => setModalType('decision')}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition-colors disabled:opacity-50 ml-auto"
        >
          <Send className="h-4 w-4" />
          <span>Record Custom Decision</span>
        </button>
      </div>

      <p className="text-[11px] text-slate-400 font-mono">
        * Prototype only — no real settlement action is executed.
      </p>

      {/* Input Modal */}
      {modalType && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-surface-100 border border-surface-borderLight rounded-xl p-5 max-w-md w-full space-y-4 shadow-2xl animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-surface-border/60 pb-2.5">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                <span>
                  {modalType === 'reject' && 'Reject Recommended Action'}
                  {modalType === 'rollback' && 'Rollback Previous Action'}
                  {modalType === 'decision' && 'Record Analyst Decision'}
                </span>
              </h3>
              <button
                onClick={() => setModalType(null)}
                className="text-slate-400 hover:text-slate-200 text-xs px-1"
              >
                ✕
              </button>
            </div>

            {modalType === 'decision' && (
              <div className="space-y-1.5 text-xs">
                <label className="text-slate-400 font-mono">Select Decision:</label>
                <select
                  value={selectedDecision}
                  onChange={(e) => setSelectedDecision(e.target.value as DecisionFeedback)}
                  className="w-full px-3 py-2 rounded-lg bg-surface-300 border border-surface-border text-slate-200 focus:outline-none focus:border-cyan-500 font-mono text-xs"
                >
                  <option value="CONFIRMED_FRAUD">CONFIRMED_FRAUD</option>
                  <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
                  <option value="CLEARED">CLEARED</option>
                  <option value="NEEDS_INVESTIGATION">NEEDS_INVESTIGATION</option>
                </select>
              </div>
            )}

            <div className="space-y-1.5 text-xs">
              <label className="text-slate-400 font-mono">
                {modalType === 'rollback' ? 'Rollback Justification (Required):' : 'Analyst Rationale / Justification (Required):'}
              </label>
              <textarea
                rows={3}
                value={justification}
                onChange={(e) => setJustification(e.target.value)}
                placeholder="Enter detailed justification for the immutable audit trail..."
                className="w-full px-3 py-2 rounded-lg bg-surface-300 border border-surface-border text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-xs leading-relaxed"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setModalType(null)}
                className="px-3 py-1.5 rounded-lg hover:bg-surface-50 text-slate-400 text-xs"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={!justification.trim() || isLoading}
                className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs disabled:opacity-50 transition-colors"
              >
                {isLoading ? 'Recording...' : 'Submit Decision'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
