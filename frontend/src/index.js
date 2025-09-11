import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// Disable React error overlay for ResizeObserver errors in development
if (process.env.NODE_ENV === 'development') {
  const originalError = console.error;
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('ResizeObserver loop completed with undelivered notifications')
    ) {
      return; // Suppress ResizeObserver errors completely
    }
    originalError.apply(console, args);
  };

  // Disable the React error overlay for ResizeObserver errors specifically
  window.addEventListener('error', (event) => {
    if (event.message && event.message.includes('ResizeObserver loop completed with undelivered notifications')) {
      event.stopImmediatePropagation();
      event.preventDefault();
    }
  });

  // Override React's error reporting for ResizeObserver errors
  const originalReportError = window.reportError;
  if (originalReportError) {
    window.reportError = (error) => {
      if (error && error.message && error.message.includes('ResizeObserver')) {
        return; // Don't report ResizeObserver errors
      }
      return originalReportError(error);
    };
  }
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
