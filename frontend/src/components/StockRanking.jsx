import PropTypes from "prop-types";
import Tooltip from "./Tooltip";
import FilterBar from "./FilterBar";
import ScoreExplanationModal from "./ScoreExplanationModal";
import AssetContextButton from "./AssetContextButton";
import RiskBadge from "./RiskBadge";
import React, { useState, useMemo, useCallback } from "react";

const StockRanking = React.memo(function StockRanking({
  results,
  tickerDetails,
  currentPage,
  itemsPerPage,
  onPageChange,
  onRowClick,
}) {
  const [filteredResults, setFilteredResults] = useState(results);
  const [selectedScore, setSelectedScore] = useState(null);
  const [selectedTicker, setSelectedTicker] = useState(null);

  // Prepare enriched stock data with details for filtering
  const enrichedStocks = useMemo(() => {
    return results.map((r) => ({
      ...r,
      name: tickerDetails[r.ticker]?.name || "",
      country: tickerDetails[r.ticker]?.country || "",
      sector: tickerDetails[r.ticker]?.sector || "",
      price: tickerDetails[r.ticker]?.price || 0,
      volume: tickerDetails[r.ticker]?.volume || 0,
      market_cap: tickerDetails[r.ticker]?.market_cap || 0,
      change: tickerDetails[r.ticker]?.change || 0,
      rank: results.indexOf(r) + 1,
    }));
  }, [results, tickerDetails]);

  const handleFilterChange = useCallback(
    (filtered) => {
      setFilteredResults(filtered);
      onPageChange(1); // Reset to page 1 when filters change
    },
    [onPageChange]
  );

  const formatNumber = useCallback((num) => {
    if (!num) return "N/A";
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toFixed(2)}`;
  }, []);

  const getRankBadgeClass = useCallback((rank) => {
    if (rank === 1) return "rank-badge gold";
    if (rank === 2) return "rank-badge silver";
    if (rank === 3) return "rank-badge bronze";
    return "rank-badge";
  }, []);

  const totalPages = useMemo(
    () => Math.ceil(filteredResults.length / itemsPerPage),
    [filteredResults.length, itemsPerPage]
  );
  const paginatedResults = useMemo(
    () => filteredResults.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage),
    [filteredResults, currentPage, itemsPerPage]
  );

  return (
    <>
      {/* Filter Bar */}
      <FilterBar
        stocks={enrichedStocks}
        onFilterChange={handleFilterChange}
        showCountryFilter={true}
        showSectorFilter={true}
        showMarketCapFilter={true}
      />

      {/* Results Summary */}
      {filteredResults.length < results.length && (
        <div
          style={{
            padding: "12px 16px",
            background: "linear-gradient(135deg, #667eea15 0%, #764ba215 100%)",
            border: "2px solid #667eea30",
            borderRadius: "8px",
            marginBottom: "16px",
            fontSize: "0.9rem",
            color: "#667eea",
            fontWeight: "600",
          }}
        >
          📊 Showing {filteredResults.length} of {results.length} stocks
        </div>
      )}

      {/* Ranked Stocks Table */}
      <h2>Ranked Stocks</h2>
      <div className="table-wrapper">
        <table aria-label="Ranked stocks results table">
          <thead>
            <tr>
              <th scope="col">Rank</th>
              <th scope="col">Stock</th>
              <th scope="col">Name</th>
              <th scope="col">Country</th>
              <th scope="col">
                <Tooltip
                  content="Composite Score (0-100) combining Technical Signals (40%), ML Model (30%), Momentum (20%), and Market Regime (10%). 80+ is Strong BUY, 65-79 is BUY, 45-64 is HOLD, 35-44 Consider Selling, below 35 is SELL."
                  position="top"
                >
                  Score ⓘ
                </Tooltip>
              </th>
              <th scope="col">
                <Tooltip
                  content="Risk Score (0-100) based on Volatility (40%), Max Drawdown (35%), and Correlation to S&P 500 (25%). LOW (0-40) = Safe, MEDIUM (41-70) = Standard, HIGH (71-100) = Reduce position size."
                  position="top"
                >
                  Risk ⓘ
                </Tooltip>
              </th>
              <th scope="col">Signal</th>
              <th scope="col">Price</th>
              <th scope="col">
                <Tooltip
                  content="Daily price change percentage. Positive (+) values indicate the stock is up today, negative (-) values mean it's down. Strong moves are typically ±3% or more for established stocks."
                  position="top"
                >
                  Change % ⓘ
                </Tooltip>
              </th>
              <th scope="col">Volume</th>
              <th scope="col">Market Cap</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {paginatedResults.map((r) => {
              const detail = tickerDetails[r.ticker] || {};
              const changeClass =
                detail.change > 0 ? "positive" : detail.change < 0 ? "negative" : "";

              return (
                <tr
                  key={r.ticker}
                  onClick={() => onRowClick(r.ticker)}
                  style={{ cursor: "pointer" }}
                  title="Click for detailed information"
                >
                  <td>
                    <span className={getRankBadgeClass(r.rank)}>{r.rank}</span>
                  </td>
                  <td>
                    <span className="ticker-symbol">{r.ticker}</span>
                  </td>
                  <td>{detail.name || "N/A"}</td>
                  <td>
                    <span className="country-tag">{detail.country || "N/A"}</span>
                  </td>
                  <td>
                    <Tooltip
                      content={`
                      Composite Score: ${r.composite_score || (r.prob * 100).toFixed(1)}/100

                      Click "Explain" button to see full breakdown.
                    `}
                      position="top"
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span
                          className={
                            (r.composite_score || r.prob * 100) >= 80
                              ? "score-strong-buy"
                              : (r.composite_score || r.prob * 100) >= 65
                                ? "score-buy"
                                : ""
                          }
                        >
                          {r.composite_score
                            ? r.composite_score.toFixed(1)
                            : (r.prob * 100).toFixed(1)}
                        </span>
                        <button
                          className="btn-explain-score"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedTicker(r.ticker);
                            setSelectedScore(r);
                          }}
                          title="Explain score breakdown"
                        >
                          📊
                        </button>
                      </div>
                    </Tooltip>
                  </td>
                  <td>
                    {/* Phase 4: Risk Score Badge */}
                    <RiskBadge
                      score={r.risk_score || 50}
                      level={r.risk_level || "MEDIUM"}
                      breakdown={r.risk_breakdown}
                      compact={true}
                    />
                  </td>
                  <td>
                    <span className={`signal-badge signal-${(r.signal || r.action).toLowerCase()}`}>
                      {r.signal || r.action}
                    </span>
                  </td>
                  <td>{detail.price ? `$${detail.price.toFixed(2)}` : "N/A"}</td>
                  <td>
                    <Tooltip
                      content={`${
                        detail.change
                          ? detail.change > 0
                            ? `+${detail.change.toFixed(2)}%`
                            : `${detail.change.toFixed(2)}%`
                          : "N/A"
                      } daily change. ${
                        detail.change > 3
                          ? "🚀 Strong upward move!"
                          : detail.change > 0
                            ? "✅ Positive momentum"
                            : detail.change < -3
                              ? "⚠️ Significant drop"
                              : detail.change < 0
                                ? "⬇️ Slight decline"
                                : "No change"
                      }`}
                      position="top"
                    >
                      <span className={changeClass}>
                        {detail.change
                          ? `${detail.change > 0 ? "+" : ""}${detail.change.toFixed(2)}%`
                          : "N/A"}
                      </span>
                    </Tooltip>
                  </td>
                  <td>{detail.volume ? detail.volume.toLocaleString() : "N/A"}</td>
                  <td>{formatNumber(detail.market_cap)}</td>
                  <td>
                    <AssetContextButton ticker={r.ticker} companyName={detail.name} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {filteredResults.length > itemsPerPage && (
        <div className="pagination">
          <button
            onClick={() => onPageChange(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
          >
            ← Previous
          </button>
          <div className="page-selector">
            <span className="page-info">Page</span>
            <select
              value={currentPage}
              onChange={(e) => onPageChange(Number(e.target.value))}
              className="page-dropdown"
            >
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
                <option key={pageNum} value={pageNum}>
                  {pageNum}
                </option>
              ))}
            </select>
            <span className="page-info">of {totalPages}</span>
          </div>
          <button
            onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage >= totalPages}
          >
            Next →
          </button>
        </div>
      )}

      {/* No Results Message */}
      {filteredResults.length === 0 && (
        <div
          style={{
            textAlign: "center",
            padding: "40px 20px",
            color: "#666",
          }}
        >
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>🔍</div>
          <h3 style={{ margin: "0 0 8px 0", color: "#333" }}>No stocks match your filters</h3>
          <p style={{ margin: 0, fontSize: "0.9rem" }}>
            Try adjusting your search or filter criteria
          </p>
        </div>
      )}

      {/* Score Explanation Modal */}
      {selectedScore && (
        <ScoreExplanationModal
          ticker={selectedTicker}
          scoreData={selectedScore}
          onClose={() => {
            setSelectedScore(null);
            setSelectedTicker(null);
          }}
        />
      )}
    </>
  );
});

StockRanking.propTypes = {
  results: PropTypes.arrayOf(
    PropTypes.shape({
      ticker: PropTypes.string.isRequired,
      prob: PropTypes.number.isRequired,
    })
  ).isRequired,
  tickerDetails: PropTypes.objectOf(
    PropTypes.shape({
      name: PropTypes.string,
      country: PropTypes.string,
      price: PropTypes.number,
      change: PropTypes.number,
      volume: PropTypes.number,
      market_cap: PropTypes.number,
    })
  ).isRequired,
  currentPage: PropTypes.number.isRequired,
  itemsPerPage: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  onRowClick: PropTypes.func.isRequired,
};

export default StockRanking;
