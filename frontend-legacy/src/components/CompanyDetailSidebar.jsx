import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import PriceChart from "./PriceChart";
import NewsPanel from "./NewsPanel";

function formatNumber(num) {
  if (!num) return "N/A";
  if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
  if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
  if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
  return `$${num.toLocaleString()}`;
}

// Generate mock historical data for demo (replace with real API call)
function generateMockPriceHistory(currentPrice, days = 30) {
  if (!currentPrice) return [];

  const data = [];
  const today = new Date();
  let price = currentPrice * 0.9; // Start 10% lower than current

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);

    // Random walk with slight upward trend
    const change = (Math.random() - 0.48) * 0.05; // Slight upward bias
    price = price * (1 + change);

    data.push({
      date: date.toISOString().split("T")[0],
      price: parseFloat(price.toFixed(2)),
    });
  }

  // Ensure last price matches current price
  data[data.length - 1].price = currentPrice;

  return data;
}

function CompanyDetailSidebar({ company, onClose }) {
  const [priceHistory, setPriceHistory] = useState([]);
  const [chartPeriod, setChartPeriod] = useState(30); // 30, 90, or 180 days

  useEffect(() => {
    if (company && company.price) {
      // TODO: Replace with real API call
      // const fetchHistory = async () => {
      //   const response = await api.getPriceHistory(company.ticker, chartPeriod)
      //   setPriceHistory(response.data)
      // }
      // fetchHistory()

      // For now, use mock data
      setPriceHistory(generateMockPriceHistory(company.price, chartPeriod));
    }
  }, [company, chartPeriod]);
  if (!company) return null;

  return (
    <>
      <div className="sidebar-overlay" onClick={onClose} aria-hidden="true"></div>
      <aside className="sidebar" role="complementary" aria-labelledby="sidebar-title">
        <button className="sidebar-close" onClick={onClose} aria-label="Close company details">
          ×
        </button>

        {company.loading ? (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <span className="spinner"></span>
            <p>Loading company details...</p>
          </div>
        ) : company.error ? (
          <div style={{ padding: "20px", color: "#e74c3c" }} role="alert">
            <p>{company.error}</p>
          </div>
        ) : (
          <div className="sidebar-content">
            <h2 id="sidebar-title">{company.ticker}</h2>
            <p className="company-name">{company.name || "N/A"}</p>
            {company.country && <p className="company-country">🌍 {company.country}</p>}

            <div className="detail-section">
              <h3>🎯 Trading Signal</h3>
              <div
                className={`signal-badge signal-${company.signal?.toLowerCase().replace(/ /g, "-")}`}
              >
                {company.signal}
              </div>
              <p className="probability">
                ML Probability: {company.prob ? `${(company.prob * 100).toFixed(2)}%` : "N/A"}
              </p>
            </div>

            <div className="detail-section">
              <h3>💰 Price Information</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">Current Price</span>
                  <span className="detail-value">
                    {company.price ? `$${company.price.toFixed(2)}` : "N/A"}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Change %</span>
                  <span
                    className={`detail-value ${company.change > 0 ? "positive" : company.change < 0 ? "negative" : ""}`}
                  >
                    {company.change
                      ? `${company.change > 0 ? "+" : ""}${company.change.toFixed(2)}%`
                      : "N/A"}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">52-Week High</span>
                  <span className="detail-value">
                    {company.fifty_two_week_high
                      ? `$${company.fifty_two_week_high.toFixed(2)}`
                      : "N/A"}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">52-Week Low</span>
                  <span className="detail-value">
                    {company.fifty_two_week_low
                      ? `$${company.fifty_two_week_low.toFixed(2)}`
                      : "N/A"}
                  </span>
                </div>
              </div>
            </div>

            {/* Price Chart Section */}
            <div className="detail-section">
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "12px",
                }}
              >
                <h3 style={{ margin: 0 }}>📈 Price History</h3>
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    onClick={() => setChartPeriod(30)}
                    className={`period-btn ${chartPeriod === 30 ? "active" : ""}`}
                    style={{
                      padding: "4px 12px",
                      fontSize: "0.85rem",
                      border: chartPeriod === 30 ? "2px solid #667eea" : "2px solid #ddd",
                      background: chartPeriod === 30 ? "#667eea" : "transparent",
                      color: chartPeriod === 30 ? "white" : "#666",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontWeight: chartPeriod === 30 ? "600" : "400",
                      transition: "all 0.2s ease",
                    }}
                  >
                    1M
                  </button>
                  <button
                    onClick={() => setChartPeriod(90)}
                    className={`period-btn ${chartPeriod === 90 ? "active" : ""}`}
                    style={{
                      padding: "4px 12px",
                      fontSize: "0.85rem",
                      border: chartPeriod === 90 ? "2px solid #667eea" : "2px solid #ddd",
                      background: chartPeriod === 90 ? "#667eea" : "transparent",
                      color: chartPeriod === 90 ? "white" : "#666",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontWeight: chartPeriod === 90 ? "600" : "400",
                      transition: "all 0.2s ease",
                    }}
                  >
                    3M
                  </button>
                  <button
                    onClick={() => setChartPeriod(180)}
                    className={`period-btn ${chartPeriod === 180 ? "active" : ""}`}
                    style={{
                      padding: "4px 12px",
                      fontSize: "0.85rem",
                      border: chartPeriod === 180 ? "2px solid #667eea" : "2px solid #ddd",
                      background: chartPeriod === 180 ? "#667eea" : "transparent",
                      color: chartPeriod === 180 ? "white" : "#666",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontWeight: chartPeriod === 180 ? "600" : "400",
                      transition: "all 0.2s ease",
                    }}
                  >
                    6M
                  </button>
                </div>
              </div>
              <PriceChart data={priceHistory} width={400} height={200} color="#667eea" />
            </div>

            <div className="detail-section">
              <h3>📊 Market Data</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">Market Cap</span>
                  <span className="detail-value">{formatNumber(company.market_cap)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Volume</span>
                  <span className="detail-value">
                    {company.volume ? company.volume.toLocaleString() : "N/A"}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">P/E Ratio</span>
                  <span className="detail-value">
                    {company.pe_ratio ? company.pe_ratio.toFixed(2) : "N/A"}
                  </span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>💡 Recommendation</h3>
              <p className="recommendation-text">
                {company.signal === "STRONG BUY" &&
                  "This stock shows strong potential for outperformance based on ML analysis. Consider adding to your portfolio."}
                {company.signal === "BUY" &&
                  "Positive signals indicate good buying opportunity. Review fundamentals before investing."}
                {company.signal === "HOLD" &&
                  "Neutral signals suggest maintaining current position. Monitor for changes."}
                {company.signal === "CONSIDER SELLING" &&
                  "Weak signals detected. Consider reducing position or exiting."}
                {company.signal === "SELL" &&
                  "ML model suggests poor performance outlook. Consider exiting position."}
              </p>
            </div>

            {/* News Panel */}
            <NewsPanel ticker={company.ticker} limit={5} />
          </div>
        )}
      </aside>
    </>
  );
}

CompanyDetailSidebar.propTypes = {
  company: PropTypes.shape({
    ticker: PropTypes.string,
    name: PropTypes.string,
    country: PropTypes.string,
    signal: PropTypes.string,
    prob: PropTypes.number,
    price: PropTypes.number,
    change: PropTypes.number,
    fifty_two_week_high: PropTypes.number,
    fifty_two_week_low: PropTypes.number,
    market_cap: PropTypes.number,
    volume: PropTypes.number,
    pe_ratio: PropTypes.number,
    loading: PropTypes.bool,
    error: PropTypes.string,
  }),
  onClose: PropTypes.func.isRequired,
};

export default CompanyDetailSidebar;
