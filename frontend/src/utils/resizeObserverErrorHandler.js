/**
 * Unified ResizeObserver Error Handler
 * 
 * Provides comprehensive, production-ready ResizeObserver error suppression
 * across all browsers and environments (development and production).
 * 
 * Supports: Chrome, Firefox, Safari, iOS Safari, Android Chrome
 * 
 * Features:
 * - Universal error suppression (console, boundaries, overlays)
 * - Browser-specific handling
 * - Environment-aware logging
 * - Graceful degradation
 * - Performance optimized
 */

class ResizeObserverErrorHandler {
  constructor() {
    this.originalConsoleError = null;
    this.originalConsoleWarn = null;
    this.originalWindowError = null;
    this.originalUnhandledRejection = null;
    this.isInitialized = false;
    this.errorCount = 0;
    this.suppressedCount = 0;
    
    // Browser detection
    this.browser = this.detectBrowser();
    
    // Environment detection
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.isProduction = process.env.NODE_ENV === 'production';
  }

  detectBrowser() {
    if (typeof window === 'undefined') return 'server';
    
    const userAgent = window.navigator.userAgent;
    
    if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) {
      return userAgent.includes('Mobile') ? 'chrome-mobile' : 'chrome';
    }
    if (userAgent.includes('Firefox')) {
      return 'firefox';
    }
    if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
      return userAgent.includes('Mobile') ? 'safari-mobile' : 'safari';
    }
    if (userAgent.includes('Edg')) {
      return 'edge';
    }
    
    return 'unknown';
  }

  isResizeObserverError(error, message = '') {
    const errorMessage = error?.message || message || '';
    
    return (
      errorMessage.includes('ResizeObserver loop completed with undelivered notifications') ||
      errorMessage.includes('ResizeObserver loop limit exceeded') ||
      errorMessage.includes('ResizeObserver callback may not be called') ||
      errorMessage.includes('ResizeObserver observation completed') ||
      (errorMessage.includes('ResizeObserver') && errorMessage.includes('loop'))
    );
  }

  logSuppression(method, errorMessage) {
    this.suppressedCount++;
    
    // Only log in development for debugging
    if (this.isDevelopment && this.suppressedCount <= 5) {
      console.debug(`[ResizeObserver Suppressed via ${method}]:`, errorMessage.substring(0, 100));
    }
  }

  setupConsoleOverrides() {
    // Store original console methods
    this.originalConsoleError = console.error;
    this.originalConsoleWarn = console.warn;

    // Override console.error
    console.error = (...args) => {
      const message = args[0];
      
      if (typeof message === 'string' && this.isResizeObserverError(null, message)) {
        this.logSuppression('console.error', message);
        return;
      }
      
      // Let other errors through
      return this.originalConsoleError.apply(console, args);
    };

    // Override console.warn
    console.warn = (...args) => {
      const message = args[0];
      
      if (typeof message === 'string' && this.isResizeObserverError(null, message)) {
        this.logSuppression('console.warn', message);
        return;
      }
      
      return this.originalConsoleWarn.apply(console, args);
    };
  }

  setupWindowErrorHandlers() {
    // Global error handler
    this.originalWindowError = window.onerror;
    window.onerror = (message, source, lineno, colno, error) => {
      if (this.isResizeObserverError(error, message)) {
        this.logSuppression('window.onerror', message);
        return true; // Prevent default error handling
      }
      
      return this.originalWindowError ? 
        this.originalWindowError(message, source, lineno, colno, error) : false;
    };

    // Error event listener
    window.addEventListener('error', (event) => {
      if (this.isResizeObserverError(event.error, event.message)) {
        this.logSuppression('error-event', event.message || event.error?.message || '');
        event.preventDefault();
        event.stopPropagation();
        return false;
      }
    }, true);

    // Unhandled promise rejection handler
    this.originalUnhandledRejection = window.onunhandledrejection;
    window.onunhandledrejection = (event) => {
      if (this.isResizeObserverError(event.reason)) {
        this.logSuppression('unhandledrejection', event.reason?.message || '');
        event.preventDefault();
        return true;
      }
      
      return this.originalUnhandledRejection ? 
        this.originalUnhandledRejection(event) : false;
    };

    window.addEventListener('unhandledrejection', (event) => {
      if (this.isResizeObserverError(event.reason)) {
        this.logSuppression('unhandledrejection-event', event.reason?.message || '');
        event.preventDefault();
        event.stopPropagation();
      }
    });
  }

  setupReactErrorBoundarySupport() {
    // Override React's error reporting if available
    if (window.reportError) {
      const originalReportError = window.reportError;
      window.reportError = (error) => {
        if (this.isResizeObserverError(error)) {
          this.logSuppression('reportError', error?.message || '');
          return;
        }
        return originalReportError(error);
      };
    }

    // Handle React DevTools error overlay (development only)
    if (this.isDevelopment && window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
      const hook = window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
      
      if (hook.onErrorOverlay) {
        const originalOnErrorOverlay = hook.onErrorOverlay;
        hook.onErrorOverlay = (error) => {
          if (this.isResizeObserverError(error)) {
            this.logSuppression('react-devtools', error?.message || '');
            return;
          }
          return originalOnErrorOverlay(error);
        };
      }
    }
  }

  setupBrowserSpecificHandlers() {
    switch (this.browser) {
      case 'chrome':
      case 'chrome-mobile':
        this.setupChromeSpecificHandlers();
        break;
      case 'firefox':
        this.setupFirefoxSpecificHandlers();
        break;
      case 'safari':
      case 'safari-mobile':
        this.setupSafariSpecificHandlers();
        break;
      default:
        // Universal handlers already set up
        break;
    }
  }

  setupChromeSpecificHandlers() {
    // Chrome-specific ResizeObserver error patterns
    const chromePatterns = [
      'ResizeObserver loop completed with undelivered notifications',
      'ResizeObserver callback may not be called'
    ];

    // Additional Chrome error overlay suppression
    if (this.isDevelopment) {
      const originalPostMessage = window.postMessage;
      window.postMessage = function(message, ...args) {
        if (typeof message === 'object' && message?.source === 'react-devtools-content-script') {
          const payload = message?.payload;
          if (payload && typeof payload === 'string' && chromePatterns.some(pattern => payload.includes(pattern))) {
            return; // Suppress React DevTools error messages
          }
        }
        return originalPostMessage.call(this, message, ...args);
      };
    }
  }

  setupFirefoxSpecificHandlers() {
    // Firefox-specific handling
    // Firefox may report ResizeObserver errors differently
    const originalFirefoxError = console.error;
    console.error = (...args) => {
      const message = args.join(' ');
      if (message.includes('ResizeObserver') && message.includes('callback')) {
        this.logSuppression('firefox-console', message);
        return;
      }
      return originalFirefoxError.apply(console, args);
    };
  }

  setupSafariSpecificHandlers() {
    // Safari-specific handling
    // Safari may have different ResizeObserver implementation
    if (window.safari) {
      // Safari browser specific handling
      const originalSafariError = console.error;
      console.error = (...args) => {
        const message = args[0];
        if (typeof message === 'string' && message.includes('ResizeObserver')) {
          this.logSuppression('safari-console', message);
          return;
        }
        return originalSafariError.apply(console, args);
      };
    }
  }

  initialize() {
    if (this.isInitialized) {
      console.warn('[ResizeObserverErrorHandler] Already initialized');
      return;
    }

    if (typeof window === 'undefined') {
      console.warn('[ResizeObserverErrorHandler] Cannot initialize in server environment');
      return;
    }

    try {
      // Set up all error handlers
      this.setupConsoleOverrides();
      this.setupWindowErrorHandlers();
      this.setupReactErrorBoundarySupport();
      this.setupBrowserSpecificHandlers();

      this.isInitialized = true;
      
      if (this.isDevelopment) {
        console.info(`[ResizeObserverErrorHandler] Initialized for ${this.browser} in ${process.env.NODE_ENV} mode`);
      }
    } catch (error) {
      console.error('[ResizeObserverErrorHandler] Initialization failed:', error);
    }
  }

  destroy() {
    if (!this.isInitialized) return;

    try {
      // Restore original handlers
      if (this.originalConsoleError) {
        console.error = this.originalConsoleError;
      }
      if (this.originalConsoleWarn) {
        console.warn = this.originalConsoleWarn;
      }
      if (this.originalWindowError) {
        window.onerror = this.originalWindowError;
      }
      if (this.originalUnhandledRejection) {
        window.onunhandledrejection = this.originalUnhandledRejection;
      }

      this.isInitialized = false;
      
      if (this.isDevelopment) {
        console.info(`[ResizeObserverErrorHandler] Destroyed. Suppressed ${this.suppressedCount} errors.`);
      }
    } catch (error) {
      console.error('[ResizeObserverErrorHandler] Destroy failed:', error);
    }
  }

  getStats() {
    return {
      browser: this.browser,
      initialized: this.isInitialized,
      suppressedCount: this.suppressedCount,
      environment: process.env.NODE_ENV
    };
  }
}

// Create singleton instance
const resizeObserverErrorHandler = new ResizeObserverErrorHandler();

// Export both the class and singleton instance
export { ResizeObserverErrorHandler, resizeObserverErrorHandler };

// Auto-initialize in browser environment
if (typeof window !== 'undefined') {
  // Initialize immediately
  resizeObserverErrorHandler.initialize();
  
  // Clean up on unload
  window.addEventListener('beforeunload', () => {
    resizeObserverErrorHandler.destroy();
  });
}

export default resizeObserverErrorHandler;