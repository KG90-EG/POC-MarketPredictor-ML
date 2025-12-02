import axios from 'axios'

// API base URL - use environment variable or fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
})

// API methods
export const api = {
  // Health check
  health: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Metrics
  metrics: async () => {
    const response = await apiClient.get('/metrics');
    return response.data;
  },

  // Ranking endpoints
  getRanking: (country = 'Global', tickers = '') => {
    const params = new URLSearchParams()
    if (country) params.append('country', country)
    if (tickers) params.append('tickers', tickers)
    return apiClient.get(`/ranking?${params.toString()}`)
  },

  // Single ticker info
  getTickerInfo: (ticker) => apiClient.get(`/ticker_info/${ticker}`),

  // Batch ticker info (optimized)
  getTickerInfoBatch: (tickers) =>
    apiClient.post('/ticker_info_batch', tickers),

  // Prediction for single ticker
  predictTicker: (ticker) => apiClient.get(`/predict_ticker/${ticker}`),

  // AI analysis
  analyze: (ranking, userContext = null) =>
    apiClient.post('/analyze', {
      ranking,
      user_context: userContext,
    }),

  // Models info
  getModels: () => apiClient.get('/models'),

  // Crypto/Digital Assets endpoints
  getCryptoRanking: (cryptoIds = '', includeNft = true, minProbability = 0.0, limit = 50) => {
    const params = new URLSearchParams()
    if (cryptoIds) params.append('crypto_ids', cryptoIds)
    params.append('include_nft', includeNft)
    params.append('min_probability', minProbability)
    params.append('limit', limit)
    return apiClient.get(`/crypto/ranking?${params.toString()}`)
  },

  searchCrypto: (query) => {
    const params = new URLSearchParams()
    params.append('query', query)
    return apiClient.get(`/crypto/search?${params.toString()}`)
  },

  getCryptoDetails: (cryptoId) => apiClient.get(`/crypto/details/${cryptoId}`),

  // Watchlist endpoints
  getWatchlists: (userId = 'default_user') =>
    apiClient.get(`/watchlists?user_id=${userId}`),

  createWatchlist: (userId, data) =>
    apiClient.post(`/watchlists?user_id=${userId}`, data),

  getWatchlist: (userId, watchlistId) =>
    apiClient.get(`/watchlists/${watchlistId}?user_id=${userId}`),

  updateWatchlist: (userId, watchlistId, data) =>
    apiClient.put(`/watchlists/${watchlistId}?user_id=${userId}`, data),

  deleteWatchlist: (userId, watchlistId) =>
    apiClient.delete(`/watchlists/${watchlistId}?user_id=${userId}`),

  addStockToWatchlist: (userId, watchlistId, data) =>
    apiClient.post(`/watchlists/${watchlistId}/stocks?user_id=${userId}`, data),

  removeStockFromWatchlist: (userId, watchlistId, ticker) =>
    apiClient.delete(`/watchlists/${watchlistId}/stocks/${ticker}?user_id=${userId}`),
}

// Convenience functions for watchlist operations
export const fetchWatchlists = async (userId = 'default_user') => {
  const response = await api.getWatchlists(userId);
  return response.data;
};

export const createWatchlist = async (userId, data) => {
  const response = await api.createWatchlist(userId, data);
  return response.data;
};

export const deleteWatchlist = async (userId, watchlistId) => {
  const response = await api.deleteWatchlist(userId, watchlistId);
  return response.data;
};

export const addStockToWatchlist = async (userId, watchlistId, data) => {
  const response = await api.addStockToWatchlist(userId, watchlistId, data);
  return response.data;
};

export const removeStockFromWatchlist = async (userId, watchlistId, ticker) => {
  const response = await api.removeStockFromWatchlist(userId, watchlistId, ticker);
  return response.data;
}

// Error handler helper
export const handleApiError = (error, fallbackMessage = 'API request failed') => {
  console.error(fallbackMessage, error)

  if (error.response) {
    // Server responded with error status
    const detail = error.response.data?.detail || error.response.statusText
    return {
      status: error.response.status,
      message: detail,
      isRateLimit: error.response.status === 429,
    }
  } else if (error.request) {
    // Request made but no response
    return {
      status: 0,
      message: 'No response from server. Please check your connection.',
      isNetworkError: true,
    }
  } else {
    // Error setting up request
    return {
      status: 0,
      message: error.message || fallbackMessage,
      isClientError: true,
    }
  }
}

export default api
