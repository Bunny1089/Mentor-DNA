import React from 'react';
import { IndianRupee } from 'lucide-react';
import type { BusinessImpact } from '../../types';

export const BusinessImpactCard: React.FC<{ impact: BusinessImpact | null | undefined }> = ({ impact }) => {
  if (!impact) return null;

  return (
    <div className="p-4 rounded-xl border border-surface-border bg-surface-200/90 space-y-4">
      <div className="flex items-center justify-between border-b border-surface-border/70 pb-2.5">
        <div className="flex items-center gap-2">
          <IndianRupee className="h-4 w-4 text-emerald-400" />
          <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider">Financial Exposure & Loss Impact</h4>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-300 border border-surface-border text-slate-400">
          Estimated Impact (Controlled Simulation)
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
        <div className="p-3 rounded-lg bg-surface-300/80 border border-surface-border/60">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Processed Volume</span>
          <span className="text-slate-100 font-bold text-sm">₹{impact.total_processed_volume.toLocaleString('en-IN')}</span>
        </div>

        <div className="p-3 rounded-lg bg-surface-300/80 border border-surface-border/60">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Suspicious Volume</span>
          <span className="text-red-400 font-bold text-sm">₹{impact.suspicious_volume.toLocaleString('en-IN')}</span>
        </div>

        <div className="p-3 rounded-lg bg-surface-300/80 border border-surface-border/60">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Estimated Exposure</span>
          <span className="text-orange-400 font-bold text-sm">₹{impact.estimated_exposure.toLocaleString('en-IN')}</span>
        </div>

        <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-800/40">
          <span className="text-[10px] text-emerald-400 uppercase tracking-wider block">Potential Loss Prevented</span>
          <span className="text-emerald-400 font-bold text-sm">₹{impact.potential_loss_prevented.toLocaleString('en-IN')}</span>
        </div>
      </div>
    </div>
  );
};
