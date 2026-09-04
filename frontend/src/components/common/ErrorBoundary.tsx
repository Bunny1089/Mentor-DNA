import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
  fallbackMessage?: string;
  onReset?: () => void;
  isComponentLevel?: boolean;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an unhandled rendering error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.isComponentLevel) {
        return (
          <div className="p-6 rounded border border-stone-800 bg-stone-900/60 text-stone-300 flex flex-col items-center justify-center text-center space-y-3 min-h-[160px]">
            <AlertTriangle className="w-6 h-6 text-amber-500" />
            <div className="space-y-1">
              <h4 className="font-sans font-medium text-stone-200 text-sm">
                {this.props.fallbackTitle || 'Component Rendering Paused'}
              </h4>
              <p className="font-sans text-xs text-stone-400 max-w-sm">
                {this.props.fallbackMessage || 'An unexpected rendering error occurred in this view module.'}
              </p>
            </div>
            <button
              onClick={this.handleReset}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-stone-800 hover:bg-stone-700 text-stone-200 text-xs font-sans transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Component</span>
            </button>
          </div>
        );
      }

      return (
        <div className="min-h-screen bg-stone-950 text-stone-100 flex items-center justify-center p-6">
          <div className="max-w-md w-full p-8 rounded-lg border border-stone-800 bg-stone-900/90 text-center space-y-5 shadow-2xl">
            <div className="w-12 h-12 rounded-full bg-red-950/60 border border-red-800/40 text-red-400 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div className="space-y-2">
              <h2 className="font-serif text-2xl text-stone-100">
                {this.props.fallbackTitle || 'Workbench View Recovered'}
              </h2>
              <p className="font-sans text-sm text-stone-400 leading-relaxed">
                {this.props.fallbackMessage ||
                  'The application caught an unhandled interface exception. Your data and background intelligence remain safe.'}
              </p>
            </div>
            {this.state.error && (
              <div className="p-3 bg-stone-950 rounded border border-stone-800 text-left">
                <p className="font-mono text-xs text-stone-400 truncate">
                  {this.state.error.message}
                </p>
              </div>
            )}
            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={this.handleReset}
                className="inline-flex items-center gap-2 px-4 py-2 rounded bg-stone-200 hover:bg-white text-stone-950 font-sans font-medium text-sm transition-colors cursor-pointer"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Reload Workbench</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
