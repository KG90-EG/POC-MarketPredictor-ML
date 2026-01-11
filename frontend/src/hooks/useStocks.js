/**
 * Custom React hooks for state management and API interactions
 */
import { useState, useEffect, useCallback } from "react";
import { api, handleApiError } from "../api";

/**
 * Hook for managing stock rankings with loading and error states
 */
export function useStockRanking(initialViews = ["Global"]) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedViews, setSelectedViews] = useState(initialViews);

  const fetchRanking = useCallback(
    async (views = selectedViews) => {
      setLoading(true);
      setError(null);

      try {
        // Fetch ranking for each selected view and merge
        const allRankings = [];
        for (const view of views) {
          const resp = await api.getRanking(view);
          allRankings.push(...resp.data.ranking);
        }

        // Remove duplicates and re-sort by probability
        const uniqueRankings = Array.from(
          new Map(allRankings.map((item) => [item.ticker, item])).values()
        ).sort((a, b) => b.prob - a.prob);

        setResults(uniqueRankings);
        return uniqueRankings;
      } catch (e) {
        const errorInfo = handleApiError(e, "Failed to fetch rankings");
        setError(errorInfo);
        throw errorInfo;
      } finally {
        setLoading(false);
      }
    },
    [selectedViews]
  );

  return {
    results,
    loading,
    error,
    selectedViews,
    setSelectedViews,
    fetchRanking,
    refresh: () => fetchRanking(selectedViews),
  };
}

/**
 * Hook for batch fetching ticker details
 */
export function useTickerDetails(tickers = []) {
  const [details, setDetails] = useState({});
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [error, setError] = useState(null);

  const fetchDetails = useCallback(async (tickerList = tickers) => {
    if (!tickerList || tickerList.length === 0) {
      return;
    }

    setLoading(true);
    setError(null);
    setProgress({ current: 0, total: tickerList.length });

    try {
      const batchResp = await api.getTickerInfoBatch(tickerList);
      const { results: batchResults, errors } = batchResp.data;

      if (Object.keys(errors).length > 0) {
        console.warn("Some tickers failed to load:", errors);
      }

      setDetails(batchResults || {});
      setProgress({
        current: Object.keys(batchResults || {}).length,
        total: tickerList.length,
      });

      return batchResults;
    } catch (e) {
      const errorInfo = handleApiError(e, "Failed to fetch ticker details");
      console.warn("Batch fetch failed, attempting sequential fetch", errorInfo);

      // Clear error since we're falling back
      setError(null);

      // Fallback to sequential fetching
      await fetchDetailsSequential(tickerList);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchDetailsSequential = async (tickerList) => {
    const newDetails = {};
    for (let i = 0; i < tickerList.length; i++) {
      const ticker = tickerList[i];
      setProgress({ current: i + 1, total: tickerList.length });

      try {
        const infoResp = await api.getTickerInfo(ticker);
        newDetails[ticker] = infoResp.data;
      } catch (e) {
        console.error(`Failed to fetch info for ${ticker}`, e);
      }
    }
    setDetails(newDetails);
  };

  return {
    details,
    loading,
    progress,
    error,
    fetchDetails,
  };
}

/**
 * Hook for searching individual tickers
 */
export function useTickerSearch() {
  const [searchTicker, setSearchTicker] = useState("");
  const [searchResult, setSearchResult] = useState(null);
  const [searchDetails, setSearchDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const performSearch = useCallback(
    async (ticker = searchTicker) => {
      const t = (ticker || "").trim().toUpperCase();

      if (!t) {
        setError({ message: "Please enter a stock symbol to search" });
        return;
      }

      setLoading(true);
      setError(null);
      setSearchResult(null);
      setSearchDetails(null);

      try {
        const [infoResp, predResp] = await Promise.all([
          api.getTickerInfo(t),
          api.predictTicker(t),
        ]);

        const info = infoResp.data || {};
        const prob = predResp.data?.prob || null;

        setSearchResult({ ticker: t, prob });
        setSearchDetails({
          [t]: {
            name: info.name || "N/A",
            price: info.price || null,
            change: info.change || null,
            volume: info.volume || null,
            market_cap: info.market_cap || null,
            country: info.country || "N/A",
          },
        });
      } catch (e) {
        const errorInfo = handleApiError(e, "Search failed");
        setError(errorInfo);
      } finally {
        setLoading(false);
      }
    },
    [searchTicker]
  );

  const clearSearch = useCallback(() => {
    setSearchTicker("");
    setSearchResult(null);
    setSearchDetails(null);
    setError(null);
  }, []);

  return {
    searchTicker,
    setSearchTicker,
    searchResult,
    searchDetails,
    loading,
    error,
    performSearch,
    clearSearch,
  };
}

/**
 * Hook for AI analysis
 */
export function useAnalysis() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const requestAnalysis = useCallback(async (ranking, userContext = null) => {
    if (!ranking || ranking.length === 0) {
      setError({ message: "No ranking data available for analysis" });
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const resp = await api.analyze(ranking, userContext);
      const cachedNote = resp.data.cached ? " (cached result)" : "";
      setAnalysis(resp.data.analysis + cachedNote);
      return resp.data;
    } catch (e) {
      const errorInfo = handleApiError(e, "Analysis failed");
      setError(errorInfo);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearAnalysis = useCallback(() => {
    setAnalysis(null);
    setError(null);
  }, []);

  return {
    analysis,
    loading,
    error,
    requestAnalysis,
    clearAnalysis,
  };
}

/**
 * Hook for health status monitoring
 */
export function useHealthStatus(checkInterval = 30000) {
  const [status, setStatus] = useState("loading");
  const [healthData, setHealthData] = useState(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthResp = await api.health();
        setHealthData(healthResp);

        const allHealthy =
          healthResp.api_healthy && healthResp.model_loaded && healthResp.openai_configured;

        setStatus(allHealthy ? "healthy" : "warning");
      } catch (error) {
        setStatus("error");
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, checkInterval);

    return () => clearInterval(interval);
  }, [checkInterval]);

  return { status, healthData };
}

/**
 * Hook for local storage state persistence
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error loading ${key} from localStorage:`, error);
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (error) {
        console.warn(`Error saving ${key} to localStorage:`, error);
      }
    },
    [key, storedValue]
  );

  return [storedValue, setValue];
}

export default {
  useStockRanking,
  useTickerDetails,
  useTickerSearch,
  useAnalysis,
  useHealthStatus,
  useLocalStorage,
};
