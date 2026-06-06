import { Component, ReactNode } from 'react';

interface Props { children: ReactNode; fallback?: ReactNode; }
interface State { error: Error | null; }

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  render() {
    if (this.state.error) {
      return this.props.fallback ?? (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-8">
          <div className="card max-w-lg w-full text-center space-y-4">
            <div className="text-4xl">⚠️</div>
            <h1 className="text-xl font-bold text-navy-700">Something went wrong</h1>
            <p className="text-sm text-gray-500">{this.state.error.message}</p>
            <button
              onClick={() => { this.setState({ error: null }); window.location.reload(); }}
              className="btn-primary"
            >
              Reload page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
