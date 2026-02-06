import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";
import { initSentry, SentryErrorBoundary } from "./sentry";

// Initialize Sentry error tracking
initSentry();

createRoot(document.getElementById("root")).render(
  <SentryErrorBoundary fallback={<div>An error occurred. Please refresh the page.</div>}>
    <App />
  </SentryErrorBoundary>
);
