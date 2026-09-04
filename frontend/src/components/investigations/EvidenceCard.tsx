import React from 'react';
import { AlertOctagon, AlertTriangle, CheckCircle2 } from 'lucide-react';
import type { EvidenceItem } from '../../types';

export const EvidenceCard: React.FC<{ evidence: EvidenceItem }> = ({ evidence }) => {
  const severityConfig = {
    CRITICAL: {
      border: 'border-red-600/50 bg-red-950/20 text-red-400',
      icon: AlertOctagon,
      iconColor: 'text-red-500',
      badge: 'bg-red-950 text-red-400 border-red-800',
    },
    HIGH: {
      border: 'border-orange-600/50 bg-orange-950/20 text-orange-400',
      icon: AlertTriangle,
      iconColor: 'text-orange-500',
      badge: 'bg-orange-950 text-orange-400 border-orange-800',
    },
    MEDIUM: {
      border: 'border-amber-600/50 bg-amber-950/20 text-amber-400',
      icon: AlertTriangle,
      iconColor: 'text-amber-500',
      badge: 'bg-amber-950 text-amber-400 border-amber-800',
    },
    LOW: {
      border: 'border-emerald-600/50 bg-emerald-950/20 text-emerald-400',
      icon: CheckCircle2,
      iconColor: 'text-emerald-500',
      badge: 'bg-emerald-950 text-emerald-400 border-emerald-800',
    },
  };

  const config = severityConfig[evidence.severity] || severityConfig.LOW;
  const Icon = config.icon;

  return (
    <div className={`p-4 rounded-xl border ${config.border} space-y-3 transition-all duration-150`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <Icon className={`h-4 w-4 shrink-0 ${config.iconColor}`} />
          <h4 className="text-sm font-semibold text-slate-100">{evidence.title}</h4>
        </div>
        <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${config.badge}`}>
          {evidence.severity}
        </span>
      </div>

      {/* Observed vs Benchmark Metrics */}
      <div className="grid grid-cols-2 gap-2 p-2.5 rounded-lg bg-surface-300/80 border border-surface-border text-xs font-mono">
        <div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Observed Metric</span>
          <span className="text-slate-100 font-bold">{evidence.observed_value}</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Category Baseline</span>
          <span className="text-slate-300">{evidence.baseline_value}</span>
        </div>
      </div>

      <p className="text-xs text-slate-300 leading-relaxed font-normal">{evidence.explanation}</p>

      <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-surface-border/50">
        <span>Engine: {evidence.source}</span>
        <span>Confidence: {(evidence.confidence * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
};
