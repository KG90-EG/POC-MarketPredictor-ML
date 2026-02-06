import React, { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import { Tabs, TabPanel } from "../shared/Tabs";
import AssetCard from "./AssetCard";
import { apiClient } from "../../api";
import "./TopAssetsPanel.css";

/**
 * TopAssetsPanel - Multi-asset ranking panel with tabs
 *
 * Features:
 * - Tabs for Shares/Digital Assets/Commodities
 * - Fetches data from unified API (/api/ranking/{asset_type})
 * - Loading skeleton state
 * - Error state with retry
 * - Caches data per tab
 *
 * @param {object} props - Component props
 * @param {string} props.defaultTab - Default active tab
 * @param {function} props.onAssetSelect - Callback when asset is selected
 * @param {number} props.limit - Max assets to show per tab
 * @param {string} props.className - Additional CSS classes
 */
export function TopAssetsPanel({
  defaultTab = "shares",
  onAssetSelect,
  limit = 10,
  className = "",
}) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  const [data, setData] = useState({
    shares: null,
    digital_assets: null,
    commodities: null,
  });
  const [loading, setLoading] = useState({
    shares: false,
    digital_assets: false,
    commodities: false,
  });
  const [errors, setErrors] = useState({
    shares: null,
    digital_assets: null,
    commodities: null,
  });
  const [selectedAsset, setSelectedAsset] = useState(null);

  // Tab configuration
  const tabs = [
    { id: "shares", label: "Shares", icon: "📈", count: data.shares?.length },
    { id: "digital_assets", label: "Crypto", icon: "🪙", count: data.digital_assets?.length },
    { id: "commodities", label: "Commodities", icon: "🛢️", count: data.commodities?.length },
  ];

  // Fetch data for a specific asset type
  const fetchData = useCallback(
    async (assetType) => {
      // Skip if already loading or has data
      if (loading[assetType] || data[assetType]) return;

      setLoading((prev) => ({ ...prev, [assetType]: true }));
      setErrors((prev) => ({ ...prev, [assetType]: null }));

      try {
        const response = await apiClient.get(`/api/ranking/${assetType}`, {
          params: { limit },
        });

        // Normalize the response data
        const assets = normalizeAssets(response.data, assetType);
        setData((prev) => ({ ...prev, [assetType]: assets }));
      } catch (error) {
        console.error(`Failed to fetch ${assetType}:`, error);
        setErrors((prev) => ({
          ...prev,
          [assetType]: error.response?.data?.detail || error.message || "Failed to load data",
        }));
      } finally {
        setLoading((prev) => ({ ...prev, [assetType]: false }));
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    },
    [loading, data, limit]
  );

  // Normalize different API response formats
  const normalizeAssets = (responseData, assetType) => {
    // Handle array response
    if (Array.isArray(responseData)) {
      return responseData.map((item, index) => ({
        rank: index + 1,
        ticker: item.ticker || item.symbol || item.crypto_id,
        name: item.name || item.company_name,
        price: item.current_price || item.price,
        change: item.change_percent || item.price_change_percentage_24h || item.change,
        score: item.score || item.ai_score || 50,
        signal: item.signal || item.recommendation || "HOLD",
        riskLevel: item.risk_level || item.risk || "medium",
        assetType,
        sparklineData: item.sparkline_7d?.price || item.sparkline,
      }));
    }

    // Handle object with data array
    if (responseData.data && Array.isArray(responseData.data)) {
      return normalizeAssets(responseData.data, assetType);
    }

    // Handle object with rankings array
    if (responseData.rankings && Array.isArray(responseData.rankings)) {
      return normalizeAssets(responseData.rankings, assetType);
    }

    return [];
  };

  // Fetch data when tab changes
  useEffect(() => {
    fetchData(activeTab);
  }, [activeTab, fetchData]);

  // Handle tab change
  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
  };

  // Handle asset selection
  const handleAssetClick = (asset) => {
    setSelectedAsset(asset.ticker);
    onAssetSelect?.(asset);
  };

  // Retry failed request
  const handleRetry = (assetType) => {
    setData((prev) => ({ ...prev, [assetType]: null }));
    setErrors((prev) => ({ ...prev, [assetType]: null }));
    fetchData(assetType);
  };

  // Render content for each tab
  const renderTabContent = (assetType) => {
    if (loading[assetType]) {
      return <LoadingSkeleton count={5} />;
    }

    if (errors[assetType]) {
      return <ErrorState message={errors[assetType]} onRetry={() => handleRetry(assetType)} />;
    }

    const assets = data[assetType];
    if (!assets || assets.length === 0) {
      return <EmptyState assetType={assetType} />;
    }

    return (
      <div className="top-assets__list">
        {assets.map((asset) => (
          <AssetCard
            key={asset.ticker}
            {...asset}
            isSelected={selectedAsset === asset.ticker}
            onClick={() => handleAssetClick(asset)}
          />
        ))}
      </div>
    );
  };

  return (
    <div className={`top-assets-panel ${className}`.trim()}>
      <Tabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} fullWidth />

      <div className="top-assets__content">
        <TabPanel id="shares" activeTab={activeTab}>
          {renderTabContent("shares")}
        </TabPanel>
        <TabPanel id="digital_assets" activeTab={activeTab}>
          {renderTabContent("digital_assets")}
        </TabPanel>
        <TabPanel id="commodities" activeTab={activeTab}>
          {renderTabContent("commodities")}
        </TabPanel>
      </div>
    </div>
  );
}

/**
 * Loading skeleton for asset cards
 */
function LoadingSkeleton({ count = 5 }) {
  return (
    <div className="top-assets__list top-assets__list--loading">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="asset-card asset-card--loading">
          <div className="asset-card__rank">#-</div>
          <div className="asset-card__info">
            <div className="asset-card__header">
              <span className="asset-card__ticker">LOAD</span>
            </div>
            <div className="asset-card__name">Loading...</div>
          </div>
          <div className="asset-card__price-section">
            <div className="asset-card__price">$--</div>
            <div className="asset-card__change">--%</div>
          </div>
          <div className="asset-card__score">
            <span className="asset-card__score-value">--</span>
          </div>
          <div className="asset-card__signal">---</div>
        </div>
      ))}
    </div>
  );
}

/**
 * Error state with retry button
 */
function ErrorState({ message, onRetry }) {
  return (
    <div className="top-assets__error">
      <span className="top-assets__error-icon" aria-hidden="true">
        ⚠️
      </span>
      <p className="top-assets__error-message">{message}</p>
      <button className="top-assets__retry-btn" onClick={onRetry}>
        Try Again
      </button>
    </div>
  );
}

/**
 * Empty state when no assets found
 */
function EmptyState({ assetType }) {
  const labels = {
    shares: "stocks",
    digital_assets: "cryptocurrencies",
    commodities: "commodities",
  };

  return (
    <div className="top-assets__empty">
      <span className="top-assets__empty-icon" aria-hidden="true">
        📭
      </span>
      <p className="top-assets__empty-message">
        No {labels[assetType] || "assets"} available at the moment.
      </p>
    </div>
  );
}

TopAssetsPanel.propTypes = {
  defaultTab: PropTypes.oneOf(["shares", "digital_assets", "commodities"]),
  onAssetSelect: PropTypes.func,
  limit: PropTypes.number,
  className: PropTypes.string,
};

export default TopAssetsPanel;
