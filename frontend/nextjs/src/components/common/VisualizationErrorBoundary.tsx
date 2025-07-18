import React from 'react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class VisualizationErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-6 border border-red-200 rounded-lg bg-red-50">
          <p className="text-red-800 font-medium">Visualization Error</p>
          <p className="text-sm text-red-600 mt-1">
            We encountered an issue displaying this visualization. Our team has been notified.
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default VisualizationErrorBoundary;
