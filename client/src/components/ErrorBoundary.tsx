import { Component, ReactNode, ErrorInfo } from 'react';

interface Props { children: ReactNode; fallback?: ReactNode; name?: string; }
interface State { error: Error | null; errorInfo: ErrorInfo | null; }

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null, errorInfo: null };

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    // In production, send to error tracking service here
    console.error(`[ErrorBoundary${this.props.name ? ` (${this.props.name})` : ''}]`, error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ error: null, errorInfo: null });
  };

  render() {
    if (this.state.error) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div
          role="alert"
          aria-live="assertive"
          className="min-h-[50vh] flex items-center justify-center bg-gray-50 p-6"
        >
          <div className="card max-w-lg w-full text-center space-y-4">
            <div className="w-16 h-16 bg-status-redBg rounded-2xl flex items-center justify-center mx-auto" aria-hidden="true">
              <span className="text-3xl">⚠️</span>
            </div>
            <div>
              <h2 className="text-lg font-bold text-navy-700 mb-1">Something went wrong</h2>
              <p className="text-sm text-gray-500 leading-relaxed">
                An unexpected error occurred. Your data is safe — please try again or reload the page.
              </p>
            </div>
            {this.state.error.message && (
              <details className="text-left">
                <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-600 select-none">
                  Technical details
                </summary>
                <pre className="mt-2 text-xs bg-gray-50 border border-gray-200 rounded-lg p-3 overflow-auto max-h-32 text-status-red">
                  {this.state.error.message}
                </pre>
              </details>
            )}
            <div className="flex flex-col xs:flex-row gap-3 justify-center pt-2">
              <button onClick={this.handleReset} className="btn-secondary">
                Try again
              </button>
              <button onClick={() => window.location.reload()} className="btn-primary">
                Reload page
              </button>
            </div>
            <p className="text-xs text-gray-400">
              Prototype — NileGov Stack · Mbarara District Local Government
            </p>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
