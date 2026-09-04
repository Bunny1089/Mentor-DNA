import React from 'react';
import { ShieldCheck, RefreshCw, AlertCircle } from 'lucide-react';
import type { SystemStatus } from '../../types';

interface HeaderProps {
  title: string;
  subtitle: string;
  systemStatus: SystemStatus | null;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  systemStatus,
  onRefresh,
  isLoading = false,
}) => {
  return (
    <header className="h-14 border-b border-[#2A2D35] bg-[#1C1F26] px-6 sm:px-8 flex items-center justify-between shrink-0 sticky top-0 z-30 font-sans">
      <div>
        <h1 className="text-[14px] font-semibold text-[#E8E6DE] tracking-tight">{title}</h1>
        <p className="text-[11px] text-[#8B8F98] font-normal leading-none mt-0.5">{subtitle}</p>
      </div>

      <div className="flex items-center gap-3.5">
        {/* Prototype Safety Notice */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#20232B] border border-[#2A2D35] text-[11px] text-[#8B8F98]">
          <ShieldCheck className="h-3.5 w-3.5 text-[#B8862E]" />
          <span>Controlled benchmark prototype</span>
        </div>

        {/* Refresh Button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#20232B] border border-[#2A2D35] hover:border-[#5A5E68] text-xs text-[#E8E6DE] transition-all duration-150 active:scale-95 disabled:opacity-50 cursor-pointer"
          >
            <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin text-[#B8862E]' : 'text-[#8B8F98]'}`} />
            <span>{isLoading ? 'Syncing...' : 'Sync telemetry'}</span>
          </button>
        )}

        {/* Backend Connectivity Indicator */}
        <div className="flex items-center gap-2 pl-3 border-l border-[#2A2D35]">
          <div className="flex items-center gap-1.5 text-xs text-[#E8E6DE]">
            {systemStatus?.data_loaded ? (
              <span className="flex items-center gap-1.5 text-[#4B7A6F] font-medium text-xs">
                <span className="h-1.5 w-1.5 rounded-full bg-[#4B7A6F] animate-pulse"></span>
                <span>Live telemetry</span>
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-[#B8862E] font-medium text-xs">
                <AlertCircle className="h-3.5 w-3.5 text-[#B8862E]" />
                <span>Offline</span>
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
