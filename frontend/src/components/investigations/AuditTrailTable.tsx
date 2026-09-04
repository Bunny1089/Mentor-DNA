import React, { useState } from 'react';
import { History, ChevronDown, ChevronUp, User, Cpu } from 'lucide-react';
import type { AuditLogEntry } from '../../types';
import { StateBadge } from '../common/Badge';

export const AuditTrailTable: React.FC<{ auditLogs: AuditLogEntry[] }> = ({ auditLogs }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!auditLogs || auditLogs.length === 0) {
    return null;
  }

  return (
    <div className="rounded-xl border border-surface-border bg-surface-200/90 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between bg-surface-100/60 hover:bg-surface-100 transition-colors text-left"
      >
        <div className="flex items-center gap-2">
          <History className="h-4 w-4 text-cyan-400" />
          <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
            Immutable Audit Trail ({auditLogs.length} Events)
          </h4>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 text-slate-400" />
        ) : (
          <ChevronDown className="h-4 w-4 text-slate-400" />
        )}
      </button>

      {isExpanded && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-surface-300/80 border-b border-surface-border text-slate-400 uppercase text-[10px]">
              <tr>
                <th className="py-2.5 px-4 font-semibold">Timestamp</th>
                <th className="py-2.5 px-4 font-semibold">Event Type</th>
                <th className="py-2.5 px-4 font-semibold">Actor</th>
                <th className="py-2.5 px-4 font-semibold">State Transition</th>
                <th className="py-2.5 px-4 font-semibold">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border/50 text-slate-300">
              {auditLogs.map((log) => (
                <tr key={log.event_id} className="hover:bg-surface-300/30 transition-colors">
                  <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 font-bold text-cyan-400">
                    {log.event_type}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-slate-300">
                      {log.actor === 'SYSTEM' ? (
                        <Cpu className="h-3 w-3 text-indigo-400" />
                      ) : (
                        <User className="h-3 w-3 text-amber-400" />
                      )}
                      <span>{log.actor_id}</span>
                    </span>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    {log.previous_state && log.new_state ? (
                      <div className="flex items-center gap-1.5">
                        <StateBadge state={log.previous_state} />
                        <span className="text-slate-500">→</span>
                        <StateBadge state={log.new_state} />
                      </div>
                    ) : (
                      <span className="text-slate-500">—</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-slate-300 max-w-xs font-sans text-xs">
                    {log.description}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
