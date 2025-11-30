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
