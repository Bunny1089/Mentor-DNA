import React from 'react';
import { Clock, ShieldAlert, ArrowUpRight, Network, CheckCircle2, UserCheck } from 'lucide-react';
import type { TimelineEvent } from '../../types';

export const TimelineView: React.FC<{ timeline: TimelineEvent[] }> = ({ timeline }) => {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 text-xs font-mono">
        No telemetry events recorded in timeline.
      </div>
    );
  }

  const getEventIcon = (eventType: string) => {
    if (eventType === 'ONBOARDING') return <UserCheck className="h-3.5 w-3.5 text-blue-400" />;
    if (eventType === 'FIRST_TRANSACTION') return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />;
    if (eventType === 'VELOCITY_SPIKE') return <ArrowUpRight className="h-3.5 w-3.5 text-orange-400" />;
    if (eventType === 'NETWORK_LINKAGE') return <Network className="h-3.5 w-3.5 text-purple-400" />;
    if (eventType === 'RISK_ESCALATION') return <ShieldAlert className="h-3.5 w-3.5 text-red-400" />;
    return <Clock className="h-3.5 w-3.5 text-slate-400" />;
  };

  const getSeverityStyle = (severity: string) => {
    if (severity === 'CRITICAL') return 'border-red-500/80 bg-red-950/30';
    if (severity === 'WARNING') return 'border-amber-500/80 bg-amber-950/30';
    return 'border-surface-border bg-surface-200/60';
  };

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-surface-border">
      {timeline.map((evt, idx) => (
        <div key={evt.event_id || idx} className="relative flex items-start gap-4 group">
          {/* Timeline Node Point */}
          <div className="absolute -left-6 mt-1 flex h-5 w-5 items-center justify-center rounded-full bg-surface-100 border border-surface-borderLight shadow-sm">
            {getEventIcon(evt.event_type)}
          </div>

          <div
            className={`w-full p-3.5 rounded-xl border ${getSeverityStyle(evt.severity)} space-y-1 transition-all duration-150 group-hover:border-slate-500`}
          >
            <div className="flex items-center justify-between gap-2">
              <h5 className="text-xs font-semibold text-slate-100">{evt.title}</h5>
              <span className="text-[10px] font-mono text-slate-400 shrink-0">
                {new Date(evt.timestamp).toLocaleString()}
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-normal">{evt.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
};
