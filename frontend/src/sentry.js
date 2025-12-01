import * as Sentry from '@sentry/react'

export function initSentry() {
  // Only initialize Sentry in production or if DSN is provided
  const dsn = import.meta.env.VITE_SENTRY_DSN
  
  if (!dsn) {
    console.log('Sentry DSN not configured - error tracking disabled')
    return
  }

  Sentry.init({
    dsn,
    environment: import.meta.env.MODE,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: false,
        blockAllMedia: false,
      }),
    ],
    
    // Performance Monitoring
    tracesSampleRate: 0.1, // 10% of transactions for performance monitoring
    
    // Session Replay
    replaysSessionSampleRate: 0.1, // 10% of sessions
    replaysOnErrorSampleRate: 1.0, // 100% of sessions with errors
    
    // Release tracking
    release: import.meta.env.VITE_APP_VERSION || 'development',
    
    // Filter out unnecessary errors
    beforeSend(event, hint) {
      // Don't send events in development
      if (import.meta.env.DEV) {
        console.log('Sentry event (dev mode):', event)
        return null
      }
      
      // Filter out network errors from localhost
      if (event.exception?.values?.[0]?.value?.includes('localhost')) {
        return null
      }
      
      return event
    },
  })
}

// Error Boundary component
export const SentryErrorBoundary = Sentry.ErrorBoundary
