import React from 'react';
import { Bot, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';
import type { AICaseBriefing } from '../../types';

interface AIBriefingCardProps {
  briefing: AICaseBriefing | null | undefined;
  onGenerate: () => void;
  isLoading: boolean;
}

export const AIBriefingCard: React.FC<AIBriefingCardProps> = ({
  briefing,
  onGenerate,
  isLoading,
}) => {
  return (
    <div className="rounded-xl border border-cyan-500/30 bg-gradient-to-b from-surface-100 to-surface-200/90 p-5 space-y-4 shadow-lg shadow-cyan-950/20">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-border/80 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-cyan-950 border border-cyan-700/60 flex items-center justify-center text-cyan-400 shadow-sm">
            <Bot className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <span>AI Risk Copilot Briefing</span>
              <Sparkles className="h-3.5 w-3.5 text-cyan-400 animate-pulse" />
            </h3>
            <p className="text-[11px] text-slate-400">Grounded synthesis constrained to structured evidence inputs</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {briefing && (
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-surface-300 border border-surface-border text-cyan-300">
              Grounding: {briefing.grounding_mode === 'LLM' ? 'Gemini 1.5 Grounded' : 'Deterministic Grounded Synthesizer'}
            </span>
          )}

          <button
            onClick={onGenerate}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs shadow-md transition-all duration-150 active:scale-95 disabled:opacity-50"
          >
            <Sparkles className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>{isLoading ? 'Synthesizing...' : briefing ? 'Regenerate Brief' : 'Generate Brief'}</span>
          </button>
        </div>
      </div>

      {briefing ? (
        <div className="space-y-4 text-xs">
          {/* 1. Summary */}
          <div className="p-3.5 rounded-lg bg-surface-300/80 border border-surface-border/80 space-y-1">
            <span className="text-[10px] font-mono uppercase font-bold text-cyan-400 tracking-wider">Executive Synopsis</span>
            <p className="text-slate-200 leading-relaxed font-normal">{briefing.summary}</p>
          </div>

          {/* 2. Key Evidence Highlights */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-mono uppercase font-bold text-slate-400 tracking-wider">Grounded Evidence Highlights</span>
            <ul className="space-y-1">
              {briefing.key_evidence.map((ev, idx) => (
                <li key={idx} className="flex items-start gap-2 text-slate-300">
                  <CheckCircle2 className="h-3.5 w-3.5 text-cyan-400 shrink-0 mt-0.5" />
                  <span>{ev}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 3. Network Context & Risk Interpretation */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3 rounded-lg bg-surface-300/60 border border-surface-border space-y-1">
              <span className="text-[10px] font-mono uppercase font-bold text-indigo-400 tracking-wider">Network Context</span>
              <p className="text-slate-300 leading-relaxed">{briefing.network_context}</p>
            </div>

            <div className="p-3 rounded-lg bg-surface-300/60 border border-surface-border space-y-1">
              <span className="text-[10px] font-mono uppercase font-bold text-amber-400 tracking-wider">Risk Interpretation</span>
              <p className="text-slate-300 leading-relaxed">{briefing.risk_interpretation}</p>
            </div>
          </div>

          {/* 4. Recommended Action */}
          <div className="p-3.5 rounded-lg bg-red-950/20 border border-red-800/40 flex items-start gap-3">
            <div className="h-6 w-6 rounded bg-red-950 flex items-center justify-center shrink-0 text-red-400 mt-0.5 border border-red-700">
              <ArrowRight className="h-3.5 w-3.5" />
            </div>
            <div>
              <span className="text-[10px] font-mono uppercase font-bold text-red-400 tracking-wider block">Recommended Operational Action</span>
              <p className="text-slate-200 font-medium">{briefing.recommended_next_step}</p>
            </div>
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 pt-2 border-t border-surface-border/40">
            <span>Evidence Items Used: {briefing.evidence_count}</span>
            <span>Generated: {new Date(briefing.generated_at).toLocaleTimeString()}</span>
          </div>
        </div>
      ) : (
        <div className="p-8 text-center space-y-2">
          <Bot className="h-8 w-8 text-slate-600 mx-auto" />
          <p className="text-xs text-slate-400">Click "Generate Brief" to synthesize structured risk factors into an actionable case summary.</p>
        </div>
      )}
    </div>
  );
};
