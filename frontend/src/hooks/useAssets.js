import { useState, useEffect, useCallback, useRef } from "react";
import { apiClient } from "../api";

/**
 * useAssets - Hook for fetching asset rankings
 *
 * Features:
 * - Fetches from /api/ranking/{asset_type}
 * - Caches results (configurable stale time)
 * - Auto-refresh (configurable interval)
 * - Returns loading/error states
 *
 * @param {string} assetType - Asset type: 'shares', 'digital_assets', 'commodities'
 * @param {object} options - Hook options
 * @param {number} options.limit - Number of assets to fetch (default: 10)
 * @param {number} options.staleTime - Cache duration in ms (default: 60000 = 1 min)
 * @param {number} options.refetchInterval - Auto-refresh interval in ms (default: 300000 = 5 min)
 * @param {boolean} options.enabled - Whether to fetch data (default: true)
 */
export function useAssets(assetType, options = {}) {
  const {
    limit = 10,
    staleTime = 60 * 1000, // 1 minute
    refetchInterval = 5 * 60 * 1000, // 5 minutes
    enabled = true,
  } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastFetched, setLastFetched] = useState(null);

  // Cache ref to persist across renders
  const cacheRef = useRef({});

  // Check if cached data is still fresh
  const isCacheFresh = useCallback(() => {
    if (!lastFetched) return false;
    return Date.now() - lastFetched < staleTime;
  }, [lastFetched, staleTime]);

  // Normalize API response to consistent format
  const normalizeAssets = useCallback(
    (responseData) => {
      if (!responseData) return [];

      // Handle array response
      if (Array.isArray(responseData)) {
        return responseData.map((item, index) => ({
          rank: item.rank || index + 1,
          ticker: item.ticker || item.symbol || item.crypto_id,
          name: item.name || item.company_name,
          price: item.current_price || item.price,
          change: item.change_24h || item.change_percent || 0,
          score: item.composite_score || item.score || 0,
          signal: item.signal || item.action || "HOLD",
          assetType,
        }));
      }

      // Handle object with rankings key
      if (responseData.rankings && Array.isArray(responseData.rankings)) {
        return normalizeAssets(responseData.rankings);
      }

      return [];
    },
    [assetType]
  );

  // Fetch data from API
  const fetchData = useCallback(
    async (force = false) => {
      // Skip if not enabled
      if (!enabled) return;

      // Skip if cache is fresh (unless forced)
      if (!force && isCacheFresh() && cacheRef.current[assetType]) {
        setData(cacheRef.current[assetType]);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await apiClient.get(`/api/ranking/${assetType}`, {
          params: { limit },
        });

        const normalized = normalizeAssets(response.data);

        // Update cache
        cacheRef.current[assetType] = normalized;
        setData(normalized);
        setLastFetched(Date.now());
      } catch (err) {
        console.error(`Failed to fetch ${assetType}:`, err);
        setError(err.response?.data?.detail || err.message || `Failed to fetch ${assetType}`);
      } finally {
        setLoading(false);
      }
    },
    [assetType, enabled, isCacheFresh, limit, normalizeAssets]
  );

  // Initial fetch and refetch on asset type change
  useEffect(() => {
    if (enabled) {
      fetchData();
    }
  }, [assetType, enabled, fetchData]);

  // Auto-refresh interval
  useEffect(() => {
    if (!enabled || !refetchInterval) return;

    const interval = setInterval(() => {
      fetchData(true); // Force refresh
    }, refetchInterval);

    return () => clearInterval(interval);
  }, [enabled, refetchInterval, fetchData]);

  // Manual refetch function
  const refetch = useCallback(() => {
    return fetchData(true);
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch,
    lastFetched,
    isFresh: isCacheFresh(),
  };
}

/**
 * useMultiAssets - Hook for fetching multiple asset types at once
 *
 * @param {Array} assetTypes - Array of asset types to fetch
 * @param {object} options - Hook options (same as useAssets)
 */
export function useMultiAssets(
  assetTypes = ["shares", "digital_assets", "commodities"],
  options = {}
) {
  const [assets, setAssets] = useState({});
  const [loading, setLoading] = useState({});
  const [errors, setErrors] = useState({});

  const { limit = 10, enabled = true } = options;

  const fetchAll = useCallback(async () => {
    if (!enabled) return;

    // Set all to loading
    const loadingState = {};
    assetTypes.forEach((type) => {
      loadingState[type] = true;
    });
    setLoading(loadingState);

    // Fetch all in parallel
    const results = await Promise.allSettled(
      assetTypes.map(async (type) => {
        const response = await apiClient.get(`/api/ranking/${type}`, {
          params: { limit },
        });
        return { type, data: response.data };
      })
    );

    // Process results
    const newAssets = {};
    const newErrors = {};
    const newLoading = {};

    results.forEach((result, index) => {
      const type = assetTypes[index];
      newLoading[type] = false;

      if (result.status === "fulfilled") {
        newAssets[type] = result.value.data;
      } else {
        newErrors[type] = result.reason?.message || "Failed to fetch";
      }
    });

    setAssets(newAssets);
    setErrors(newErrors);
    setLoading(newLoading);
  }, [assetTypes, enabled, limit]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return {
    assets,
    loading,
    errors,
    refetchAll: fetchAll,
  };
}

export default useAssets;
