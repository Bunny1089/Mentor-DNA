import React from 'react';
import { AlertCircle, RefreshCw, Inbox, Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading intelligence telemetry...',
}) => (
  <div className="py-16 px-4 flex flex-col items-center justify-center text-center space-y-4">
    <div className="relative">
      <Loader2 className="w-8 h-8 text-stone-400 animate-spin" />
    </div>
    <p className="font-sans text-sm text-stone-400">{message}</p>
  </div>
);

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  isBackendUnreachable?: boolean;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Unable to Load Data',
  message = 'Failed to connect to the risk intelligence engine. Please ensure the backend is running.',
  onRetry,
  isBackendUnreachable = false,
}) => (
  <div className="py-12 px-6 rounded-lg border border-stone-800 bg-stone-900/50 flex flex-col items-center justify-center text-center space-y-4 max-w-lg mx-auto my-8">
    <div className="w-10 h-10 rounded-full bg-red-950/40 border border-red-800/30 text-red-400 flex items-center justify-center">
      <AlertCircle className="w-5 h-5" />
    </div>
    <div className="space-y-1">
      <h3 className="font-sans font-medium text-stone-200 text-base">
        {isBackendUnreachable ? 'Backend Server Unreachable' : title}
      </h3>
      <p className="font-sans text-xs text-stone-400 leading-relaxed max-w-sm">
        {isBackendUnreachable
          ? 'Unable to communicate with http://127.0.0.1:8000. Verify the backend service process is active.'
          : message}
      </p>
    </div>
    {onRetry && (
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 px-4 py-2 rounded bg-stone-800 hover:bg-stone-700 text-stone-200 font-sans text-xs font-medium transition-colors cursor-pointer border border-stone-700"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        <span>Retry Connection</span>
      </button>
    )}
  </div>
);

interface EmptyStateProps {
  title?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No Records Found',
  message = 'There are no active records matching the selected parameters or filters.',
  actionLabel,
  onAction,
}) => (
  <div className="py-14 px-6 rounded-lg border border-stone-800/80 bg-stone-900/30 flex flex-col items-center justify-center text-center space-y-3">
    <div className="w-9 h-9 rounded-full bg-stone-800/60 text-stone-400 flex items-center justify-center">
      <Inbox className="w-4 h-4" />
    </div>
    <div className="space-y-1">
      <h4 className="font-sans font-medium text-stone-300 text-sm">{title}</h4>
      <p className="font-sans text-xs text-stone-400 max-w-sm">{message}</p>
    </div>
    {actionLabel && onAction && (
      <button
        onClick={onAction}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-stone-800 hover:bg-stone-700 text-stone-300 font-sans text-xs transition-colors cursor-pointer border border-stone-700 mt-2"
      >
        <span>{actionLabel}</span>
      </button>
    )}
  </div>
);
