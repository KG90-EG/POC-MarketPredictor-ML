import React from 'react';
import PropTypes from 'prop-types';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleRetry = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1
    }));
  };

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '40px',
          maxWidth: '600px',
          margin: '100px auto',
          textAlign: 'center',
          backgroundColor: 'var(--card-bg)',
          borderRadius: '12px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ color: 'var(--error-color)', marginBottom: '20px' }}>
            ⚠️ Something went wrong
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
            The application encountered an unexpected error. You can try again or reload the page.
          </p>
          
          {this.state.error && (
            <details style={{
              marginBottom: '20px',
              padding: '15px',
              backgroundColor: 'var(--bg-color)',
              borderRadius: '8px',
              textAlign: 'left'
            }}>
              <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '10px' }}>
                Error Details
              </summary>
              <code style={{
                display: 'block',
                whiteSpace: 'pre-wrap',
                fontSize: '12px',
                color: 'var(--error-color)'
              }}>
                {this.state.error.toString()}
                {this.state.errorInfo && this.state.errorInfo.componentStack}
              </code>
            </details>
          )}

          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <button
              onClick={this.handleRetry}
              style={{
                padding: '12px 24px',
                backgroundColor: 'var(--primary-gradient)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600'
              }}
            >
              Try Again {this.state.retryCount > 0 && `(${this.state.retryCount})`}
            </button>
            <button
              onClick={this.handleReset}
              style={{
                padding: '12px 24px',
                backgroundColor: 'transparent',
                color: 'var(--text-color)',
                border: '2px solid var(--border-color)',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600'
              }}
            >
              Reload Page
            </button>
          </div>

          {this.state.retryCount > 2 && (
            <p style={{ marginTop: '20px', color: 'var(--warning-color)', fontSize: '14px' }}>
              💡 If the problem persists, try checking the backend server or your internet connection.
            </p>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired
};

export default ErrorBoundary;
