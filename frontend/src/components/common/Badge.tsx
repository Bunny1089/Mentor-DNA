import React from 'react';
import type { RiskLevel, InvestigationState } from '../../types';

interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, size = 'md' }) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs font-semibold px-2.5 py-1',
    lg: 'text-sm font-bold px-3.5 py-1.5',
  };

  const levelStyles: Record<RiskLevel, { bg: string; text: string; border: string; dot: string }> = {
    LOW: {
      bg: 'bg-emerald-950/50',
      text: 'text-emerald-400',
      border: 'border-emerald-700/50',
      dot: 'bg-emerald-500',
    },
    MEDIUM: {
      bg: 'bg-amber-950/50',
      text: 'text-amber-400',
      border: 'border-amber-700/50',
      dot: 'bg-amber-500',
    },
    HIGH: {
      bg: 'bg-orange-950/50',
      text: 'text-orange-400',
      border: 'border-orange-700/50',
      dot: 'bg-orange-500',
    },
    CRITICAL: {
      bg: 'bg-red-950/60',
      text: 'text-red-400',
      border: 'border-red-600/60',
      dot: 'bg-red-500 animate-ping',
    },
  };

  const current = levelStyles[level] || levelStyles.LOW;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${current.bg} ${current.text} ${current.border} ${sizeClasses[size]}`}
    >
      <span className="relative flex h-2 w-2">
        <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${current.dot}`}></span>
        <span className={`relative inline-flex h-2 w-2 rounded-full ${levelStyles[level]?.dot.split(' ')[0] || 'bg-emerald-500'}`}></span>
      </span>
      <span>{level}</span>
      {score !== undefined && (
        <span className="font-mono opacity-85">({score.toFixed(1)})</span>
      )}
    </span>
  );
};

export const StateBadge: React.FC<{ state: InvestigationState | string }> = ({ state }) => {
  const styles: Record<string, string> = {
    NEW: 'bg-blue-950/50 text-blue-400 border-blue-800/50',
    UNDER_REVIEW: 'bg-purple-950/50 text-purple-400 border-purple-800/50',
    ESCALATED: 'bg-orange-950/50 text-orange-400 border-orange-800/50',
    ACTION_RECOMMENDED: 'bg-amber-950/50 text-amber-400 border-amber-800/50',
    ACTIONED: 'bg-red-950/50 text-red-400 border-red-800/50',
    CLEARED: 'bg-emerald-950/50 text-emerald-400 border-emerald-800/50',
    CLOSED: 'bg-slate-900 text-slate-400 border-slate-700/50',
  };

  const style = styles[state] || 'bg-slate-900 text-slate-400 border-slate-700/50';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-mono border ${style}`}>
      {state.replace('_', ' ')}
    </span>
  );
};
