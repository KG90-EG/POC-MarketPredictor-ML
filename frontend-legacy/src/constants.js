/**
 * Application constants and configuration values
 */

// Trading signals
export const SIGNALS = {
  STRONG_BUY: "STRONG BUY",
  BUY: "BUY",
  HOLD: "HOLD",
  CONSIDER_SELLING: "CONSIDER SELLING",
  SELL: "SELL",
};

// Signal thresholds
export const SIGNAL_THRESHOLDS = {
  STRONG_BUY: 0.65,
  BUY: 0.55,
  HOLD_MIN: 0.45,
  HOLD_MAX: 0.55,
  CONSIDER_SELLING: 0.35,
};

// Signal colors
export const SIGNAL_COLORS = {
  [SIGNALS.STRONG_BUY]: "#00C853",
  [SIGNALS.BUY]: "#4CAF50",
  [SIGNALS.HOLD]: "#FFC107",
  [SIGNALS.CONSIDER_SELLING]: "#FF9800",
  [SIGNALS.SELL]: "#F44336",
};

// Health status types
export const HEALTH_STATUS = {
  HEALTHY: "healthy",
  WARNING: "warning",
  ERROR: "error",
  LOADING: "loading",
};

// Health status icons
export const HEALTH_ICONS = {
  [HEALTH_STATUS.HEALTHY]: "🟢",
  [HEALTH_STATUS.WARNING]: "🟡",
  [HEALTH_STATUS.ERROR]: "🔴",
  [HEALTH_STATUS.LOADING]: "⚪",
};

// Market views configuration
export const MARKET_VIEWS = [
  { id: "Global", label: "🌐 Global", description: "Top US stocks", flag: "🌐" },
  { id: "United States", label: "🇺🇸 United States", description: "US market leaders", flag: "🇺🇸" },
  { id: "Switzerland", label: "🇨🇭 Switzerland", description: "Swiss companies", flag: "🇨🇭" },
  { id: "Germany", label: "🇩🇪 Germany", description: "German companies", flag: "🇩🇪" },
  { id: "United Kingdom", label: "🇬🇧 United Kingdom", description: "UK companies", flag: "🇬🇧" },
  { id: "France", label: "🇫🇷 France", description: "French companies", flag: "🇫🇷" },
  { id: "Japan", label: "🇯🇵 Japan", description: "Japanese companies", flag: "🇯🇵" },
  { id: "Canada", label: "🇨🇦 Canada", description: "Canadian companies", flag: "🇨🇦" },
];

// Pagination defaults
export const PAGINATION = {
  ITEMS_PER_PAGE: 10,
  DEFAULT_PAGE: 1,
};

// API configuration
export const API_CONFIG = {
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 2,
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
};

// Table columns for stock rankings
export const TABLE_COLUMNS = [
  { key: "rank", label: "Rank", sortable: false, width: "80px" },
  { key: "ticker", label: "Ticker", sortable: true, width: "100px" },
  { key: "name", label: "Company", sortable: true, width: "auto" },
  { key: "country", label: "Country", sortable: true, width: "150px" },
  { key: "signal", label: "Signal", sortable: false, width: "130px" },
  { key: "probability", label: "Probability", sortable: true, width: "120px" },
  { key: "price", label: "Price", sortable: true, width: "100px" },
  { key: "change", label: "Change", sortable: true, width: "100px" },
  { key: "volume", label: "Volume", sortable: true, width: "120px" },
  { key: "market_cap", label: "Market Cap", sortable: true, width: "120px" },
];

// Number formatting
export const NUMBER_FORMATS = {
  DECIMAL_PLACES: 2,
  PERCENTAGE_PLACES: 1,
  LARGE_NUMBER_THRESHOLD: 1000,
};

// Local storage keys
export const STORAGE_KEYS = {
  THEME: "darkMode",
  SELECTED_VIEWS: "selectedMarketViews",
  USER_PREFERENCES: "userPreferences",
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: "⚠️ Network error: Please check your connection and try again.",
  RATE_LIMIT: "⏱️ Rate limit exceeded. Please wait a moment and try again.",
  INVALID_TICKER: "❌ Invalid ticker symbol. Please check and try again.",
  NO_DATA: "No data available. Please try again later.",
  SERVER_ERROR: "Server error. Please contact support if the issue persists.",
};

// Helper function for ticker not found error
export const getTickerNotFoundError = (ticker) =>
  `❌ Ticker "${ticker}" not found. Please check the symbol and try again.`;

// Success messages
export const SUCCESS_MESSAGES = {
  DATA_LOADED: "✓ Data loaded successfully",
  SEARCH_COMPLETE: "✓ Search completed",
  ANALYSIS_COMPLETE: "✓ Analysis completed",
};

// Keyboard shortcuts
export const KEYBOARD_SHORTCUTS = {
  SEARCH: "Enter",
  REFRESH: "r",
  HELP: "?",
  THEME_TOGGLE: "t",
  ESCAPE: "Escape",
};

// Animation durations (ms)
export const ANIMATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
};

// Breakpoints for responsive design
export const BREAKPOINTS = {
  MOBILE: 480,
  TABLET: 768,
  DESKTOP: 1024,
  WIDE: 1440,
};

// Chart colors
export const CHART_COLORS = {
  PRIMARY: "#6200ea",
  SECONDARY: "#9c27b0",
  SUCCESS: "#4CAF50",
  WARNING: "#FFC107",
  DANGER: "#F44336",
  INFO: "#2196F3",
};

// Helper functions
export const getSignalFromProbability = (prob) => {
  if (prob >= SIGNAL_THRESHOLDS.STRONG_BUY) return SIGNALS.STRONG_BUY;
  if (prob >= SIGNAL_THRESHOLDS.BUY) return SIGNALS.BUY;
  if (prob >= SIGNAL_THRESHOLDS.HOLD_MIN) return SIGNALS.HOLD;
  if (prob >= SIGNAL_THRESHOLDS.CONSIDER_SELLING) return SIGNALS.CONSIDER_SELLING;
  return SIGNALS.SELL;
};

export const getSignalColor = (signal) => {
  return SIGNAL_COLORS[signal] || "#757575";
};

export const formatNumber = (num) => {
  if (!num) return "N/A";
  if (num >= 1e12) return `$${(num / 1e12).toFixed(NUMBER_FORMATS.DECIMAL_PLACES)}T`;
  if (num >= 1e9) return `$${(num / 1e9).toFixed(NUMBER_FORMATS.DECIMAL_PLACES)}B`;
  if (num >= 1e6) return `$${(num / 1e6).toFixed(NUMBER_FORMATS.DECIMAL_PLACES)}M`;
  if (num >= NUMBER_FORMATS.LARGE_NUMBER_THRESHOLD) {
    return `$${num.toLocaleString()}`;
  }
  return `$${num.toFixed(NUMBER_FORMATS.DECIMAL_PLACES)}`;
};

export const formatPercentage = (num) => {
  if (num === null || num === undefined) return "N/A";
  return `${num >= 0 ? "+" : ""}${num.toFixed(NUMBER_FORMATS.PERCENTAGE_PLACES)}%`;
};

export default {
  SIGNALS,
  SIGNAL_THRESHOLDS,
  SIGNAL_COLORS,
  HEALTH_STATUS,
  HEALTH_ICONS,
  MARKET_VIEWS,
  PAGINATION,
  API_CONFIG,
  TABLE_COLUMNS,
  NUMBER_FORMATS,
  STORAGE_KEYS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  KEYBOARD_SHORTCUTS,
  ANIMATION,
  BREAKPOINTS,
  CHART_COLORS,
  getSignalFromProbability,
  getSignalColor,
  getTickerNotFoundError,
  formatNumber,
  formatPercentage,
};
