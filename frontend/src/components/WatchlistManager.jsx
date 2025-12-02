import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { api, apiClient, fetchWatchlists, createWatchlist, deleteWatchlist, addStockToWatchlist, removeStockFromWatchlist } from '../api';
import './WatchlistManager.css';

function WatchlistManager({ userId = 'default_user' }) {
  const [watchlists, setWatchlists] = useState([]);
  const [selectedWatchlist, setSelectedWatchlist] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWatchlistName, setNewWatchlistName] = useState('');
  const [newWatchlistDesc, setNewWatchlistDesc] = useState('');
  const [newStockTicker, setNewStockTicker] = useState('');
  const [newStockNotes, setNewStockNotes] = useState('');
  const [assetType, setAssetType] = useState('stock'); // 'stock' or 'crypto'
  const [stockData, setStockData] = useState({}); // Live prices and predictions
  const [loadingStocks, setLoadingStocks] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [popularStocks, setPopularStocks] = useState([]);
  const [popularCryptos, setPopularCryptos] = useState([]);
  const [loadingPopular, setLoadingPopular] = useState(false);

  // Fetch popular stocks and cryptos on mount
  useEffect(() => {
    fetchPopularStocks();
    fetchPopularCryptos();
  }, []);

  useEffect(() => {
    loadWatchlists();
  }, [userId]);

  const fetchPopularStocks = async () => {
    setLoadingPopular(true);
    try {
      const response = await apiClient.get('/popular_stocks?limit=50');
      setPopularStocks(response.data.stocks || []);
    } catch (err) {
      console.error('Failed to fetch popular stocks:', err);
      // Fallback to basic list if API fails
      setPopularStocks([
        { ticker: 'AAPL', name: 'Apple Inc.' },
        { ticker: 'MSFT', name: 'Microsoft Corporation' },
        { ticker: 'GOOGL', name: 'Alphabet Inc.' },
        { ticker: 'AMZN', name: 'Amazon.com Inc.' },
        { ticker: 'TSLA', name: 'Tesla Inc.' }
      ]);
    } finally {
      setLoadingPopular(false);
    }
  };

  const fetchPopularCryptos = async () => {
    try {
      const response = await apiClient.get('/popular_cryptos?limit=30');
      setPopularCryptos(response.data.cryptos || []);
    } catch (err) {
      console.error('Failed to fetch popular cryptos:', err);
      setPopularCryptos([
        { id: 'bitcoin', name: 'Bitcoin', symbol: 'BTC' },
        { id: 'ethereum', name: 'Ethereum', symbol: 'ETH' },
        { id: 'solana', name: 'Solana', symbol: 'SOL' }
      ]);
    }
  };

  const loadWatchlists = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchWatchlists(userId);
      setWatchlists(data.watchlists || []);
    } catch (err) {
      setError('Failed to load watchlists');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWatchlist = async (e) => {
    e.preventDefault();
    if (!newWatchlistName.trim()) return;

    setLoading(true);
    setError(null);
    try {
      await createWatchlist(userId, {
        name: newWatchlistName,
        description: newWatchlistDesc
      });
      setNewWatchlistName('');
      setNewWatchlistDesc('');
      setShowCreateForm(false);
      await loadWatchlists();
    } catch (err) {
      setError('Failed to create watchlist');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteWatchlist = async (watchlistId) => {
    if (!confirm('Are you sure you want to delete this watchlist?')) return;

    setLoading(true);
    setError(null);
    try {
      await deleteWatchlist(userId, watchlistId);
      if (selectedWatchlist?.id === watchlistId) {
        setSelectedWatchlist(null);
      }
      await loadWatchlists();
    } catch (err) {
      setError('Failed to delete watchlist');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAssetInputChange = async (value) => {
    setNewStockTicker(value);

    // If empty, show both stocks and cryptos
    if (!value.trim()) {
      const combined = [
        ...popularStocks.slice(0, 5),
        ...popularCryptos.slice(0, 5).map(c => ({
          ticker: c.id,
          name: `${c.name} (${c.symbol})`,
          asset_type: 'crypto'
        }))
      ];
      setFilteredStocks(combined);
      setShowDropdown(true);
      return;
    }

    // Search both stocks and cryptos simultaneously
    try {
      const [stocksRes, cryptosRes] = await Promise.all([
        apiClient.get(`/search_stocks?query=${encodeURIComponent(value)}&limit=5`).catch(() => ({ data: { stocks: [] } })),
        apiClient.get(`/search_cryptos?query=${encodeURIComponent(value)}&limit=5`).catch(() => ({ data: { cryptos: [] } }))
      ]);

      const stocks = stocksRes.data.stocks || [];
      const cryptos = cryptosRes.data.cryptos || [];

      // Combine results with asset_type marker
      const combined = [
        ...stocks.map(s => ({ ...s, asset_type: 'stock' })),
        ...cryptos.map(c => ({
          ticker: c.id,
          name: `${c.name} (${c.symbol})`,
          asset_type: 'crypto'
        }))
      ];

      setFilteredStocks(combined);
      setShowDropdown(true);
    } catch (err) {
      console.error('Search failed:', err);
      setFilteredStocks([]);
      setShowDropdown(true);
    }
  };

  const handleStockSelect = (stock) => {
    setNewStockTicker(stock.ticker);
    setNewStockNotes(stock.name);
    setAssetType(stock.asset_type || 'stock'); // Auto-detect from search result
    setShowDropdown(false);
  };

  const handleAddStock = async (e) => {
    e.preventDefault();
    if (!selectedWatchlist || !newStockTicker.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await addStockToWatchlist(userId, selectedWatchlist.id, {
        ticker: assetType === 'crypto' ? newStockTicker.toLowerCase() : newStockTicker.toUpperCase(),
        notes: newStockNotes,
        asset_type: assetType
      });

      // Show auto-correction message if ticker was corrected
      if (response.corrected_from) {
        setError(`Auto-corrected: ${response.corrected_from} → ${newStockTicker}`);
        setTimeout(() => setError(null), 3000);
      }

      setNewStockTicker('');
      setNewStockNotes('');
      setShowDropdown(false);

      // Fetch the full updated watchlist with items
      const watchlistResponse = await api.getWatchlist(userId, selectedWatchlist.id);
      const updatedWatchlist = watchlistResponse.data;
      setSelectedWatchlist(updatedWatchlist);

      // Also update the watchlists array
      await loadWatchlists();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add stock');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveStock = async (ticker) => {
    if (!selectedWatchlist) return;

    setLoading(true);
    setError(null);
    try {
      await removeStockFromWatchlist(userId, selectedWatchlist.id, ticker);

      // Fetch the full updated watchlist with items
      const response = await api.getWatchlist(userId, selectedWatchlist.id);
      const updatedWatchlist = response.data;
      setSelectedWatchlist(updatedWatchlist);

      // Also update the watchlists array
      await loadWatchlists();
    } catch (err) {
      setError('Failed to remove stock');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectWatchlist = async (watchlist) => {
    setLoading(true);
    setError(null);
    try {
      // Fetch full watchlist details with items
      const response = await api.getWatchlist(userId, watchlist.id);
      setSelectedWatchlist(response.data);

      // Fetch live data for all stocks in the watchlist
      if (response.data.items && response.data.items.length > 0) {
        await fetchStockData(response.data.items);
      }
    } catch (err) {
      setError('Failed to load watchlist details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStockData = async (items) => {
    setLoadingStocks(true);

    try {
      // Fetch data for each item based on asset type
      const dataPromises = items.map(async (item) => {
        try {
          if (item.asset_type === 'crypto') {
            // For crypto, use search endpoint which returns formatted data and get prediction
            const [searchRes, predictionRes] = await Promise.all([
              apiClient.get(`/crypto/search?query=${item.ticker}`),
              apiClient.get(`/watchlist/prediction/${item.ticker}?asset_type=crypto`).catch(() => ({ data: null }))
            ]);

            const cryptoData = searchRes.data;
            const predictionData = predictionRes.data;

            if (!cryptoData) {
              console.warn('No crypto data found for', item.ticker);
              return { ticker: item.ticker, info: null, prediction: null };
            }

            // Extract data from formatted search response
            const currentPrice = cryptoData.price || 0;
            const priceChange24h = cryptoData.change_24h || 0;
            const totalVolume = cryptoData.volume || 0;

            return {
              ticker: item.ticker,
              info: {
                name: cryptoData.name || item.ticker,
                price: currentPrice,
                change: priceChange24h,
                volume: totalVolume,
              },
              prediction: predictionData || {
                signal: 'HOLD',
                confidence: 50,
                reasoning: 'No prediction available'
              }
            };
          } else {
            // For stocks, use existing endpoints plus prediction
            const [infoRes, predictionRes] = await Promise.all([
              api.getTickerInfo(item.ticker),
              apiClient.get(`/watchlist/prediction/${item.ticker}?asset_type=stock`).catch(() => ({ data: null }))
            ]);

            return {
              ticker: item.ticker,
              info: infoRes.data,
              prediction: predictionRes.data || {
                signal: 'HOLD',
                confidence: 50,
                reasoning: 'No prediction available'
              }
            };
          }
        } catch (err) {
          console.error(`Failed to fetch data for ${item.ticker}:`, err);
          return { ticker: item.ticker, info: null, prediction: null };
        }
      });

      const results = await Promise.all(dataPromises);

      // Convert array to object for easy lookup
      const dataMap = {};
      results.forEach(result => {
        dataMap[result.ticker] = {
          info: result.info,
          prediction: result.prediction
        };
      });

      setStockData(dataMap);
    } catch (err) {
      console.error('Failed to fetch stock data:', err);
    } finally {
      setLoadingStocks(false);
    }
  };

  return (
    <div className="watchlist-manager">
      <div className="watchlist-header">
        <h2>My Watchlists</h2>
        <button
          className="btn-create"
          onClick={() => setShowCreateForm(!showCreateForm)}
          disabled={loading}
        >
          {showCreateForm ? 'Cancel' : '+ New Watchlist'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showCreateForm && (
        <form className="create-watchlist-form" onSubmit={handleCreateWatchlist}>
          <input
            type="text"
            placeholder="Watchlist name"
            value={newWatchlistName}
            onChange={(e) => setNewWatchlistName(e.target.value)}
            required
          />
          <textarea
            placeholder="Description (optional)"
            value={newWatchlistDesc}
            onChange={(e) => setNewWatchlistDesc(e.target.value)}
            rows={2}
          />
          <button type="submit" disabled={loading}>
            Create Watchlist
          </button>
        </form>
      )}

      <div className="watchlist-container">
        <div className="watchlist-sidebar">
          {loading && watchlists.length === 0 ? (
            <div className="loading">Loading...</div>
          ) : watchlists.length === 0 ? (
            <div className="empty-state">
              No watchlists yet. Create one to get started!
            </div>
          ) : (
            <ul className="watchlist-list">
              {watchlists.map((watchlist) => (
                <li
                  key={watchlist.id}
                  className={selectedWatchlist?.id === watchlist.id ? 'active' : ''}
                >
                  <div
                    className="watchlist-item"
                    onClick={() => handleSelectWatchlist(watchlist)}
                  >
                    <span className="watchlist-name">{watchlist.name}</span>
                    <span className="watchlist-count">{watchlist.item_count || 0} items</span>
                  </div>
                  <button
                    className="btn-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteWatchlist(watchlist.id);
                    }}
                    title="Delete watchlist"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="watchlist-details">
          {selectedWatchlist ? (
            <>
              <div className="details-header">
                <h3>{selectedWatchlist.name}</h3>
                {selectedWatchlist.description && (
                  <p className="description">{selectedWatchlist.description}</p>
                )}
              </div>
              <form className="add-stock-form" onSubmit={handleAddStock}>
                <div className="form-inputs">
                  <div className="stock-input-container">
                    <input
                      type="text"
                      placeholder="Search stocks or crypto (e.g., Apple, Bitcoin, AAPL, BTC)"
                      value={newStockTicker}
                      onChange={(e) => handleAssetInputChange(e.target.value)}
                      onFocus={() => {
                        // Show popular items on focus
                        const combined = [
                          ...popularStocks.slice(0, 5),
                          ...popularCryptos.slice(0, 5).map(c => ({
                            ticker: c.id,
                            name: `${c.name} (${c.symbol})`,
                            asset_type: 'crypto'
                          }))
                        ];
                        setFilteredStocks(combined);
                        setShowDropdown(true);
                      }}
                      onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
                      required
                      autoComplete="off"
                    />
                    {showDropdown && filteredStocks.length > 0 && (
                      <div className="stock-dropdown">
                        {filteredStocks.slice(0, 10).map((stock) => (
                          <div
                            key={stock.ticker}
                            className="dropdown-item"
                            onClick={() => handleStockSelect(stock)}
                          >
                            <span className="ticker">{stock.ticker}</span>
                            <span className="company-name">{stock.name}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <input
                    type="text"
                    placeholder="Notes (optional)"
                    value={newStockNotes}
                    onChange={(e) => setNewStockNotes(e.target.value)}
                  />
                  <button type="submit" disabled={loading}>
                    Add
                  </button>
                </div>
              </form>

              <div className="stocks-list">
                {loadingStocks && (
                  <div className="loading-stocks">Loading stock data...</div>
                )}
                {selectedWatchlist.items?.length > 0 ? (
                  <ul>
                    {selectedWatchlist.items.map((item) => {
                      const data = stockData[item.ticker];
                      const info = data?.info;
                      const prediction = data?.prediction;

                      // Get signal from prediction
                      const signal = prediction?.signal || 'HOLD';
                      const confidence = prediction?.confidence || 50;
                      const reasoning = prediction?.reasoning || 'No prediction available';

                      // Signal colors and icons
                      const signalConfig = {
                        'BUY': { icon: '🟢', color: '#10b981', bgColor: '#d1fae5' },
                        'SELL': { icon: '🔴', color: '#ef4444', bgColor: '#fee2e2' },
                        'HOLD': { icon: '🟡', color: '#f59e0b', bgColor: '#fef3c7' }
                      };

                      const config = signalConfig[signal] || signalConfig['HOLD'];

                      // Map backend response to expected fields
                      const price = info?.price;
                      const change = info?.change;
                      const changePercent = (change && price) ? (change / (price - change)) * 100 : 0;
                      const volume = info?.volume;

                      return (
                        <li key={item.id} className="stock-item enhanced">
                          <div className="stock-main">
                            <div className="stock-header">
                              <span className="stock-ticker">{item.ticker}</span>
                              {info?.name && (
                                <span className="stock-name">{info.name}</span>
                              )}
                              <span className="asset-badge" style={{
                                backgroundColor: item.asset_type === 'crypto' ? '#8b5cf6' : '#3b82f6',
                                color: 'white',
                                padding: '2px 8px',
                                borderRadius: '4px',
                                fontSize: '0.75rem',
                                marginLeft: '8px'
                              }}>
                                {item.asset_type === 'crypto' ? '₿ Crypto' : '📈 Stock'}
                              </span>
                            </div>

                            {info && price && (
                              <div className="stock-prices">
                                <div className="price-info">
                                  <span className="current-price">${price.toFixed(2)}</span>
                                  <span className={`price-change ${changePercent >= 0 ? 'positive' : 'negative'}`}>
                                    {changePercent >= 0 ? '▲' : '▼'}
                                    {Math.abs(changePercent).toFixed(2)}%
                                  </span>
                                </div>
                                {volume && (
                                  <div className="volume-info">
                                    Vol: {(volume / 1000000).toFixed(1)}M
                                  </div>
                                )}
                              </div>
                            )}

                            {prediction && (
                              <div className="prediction-info">
                                <div
                                  className="recommendation"
                                  style={{
                                    backgroundColor: config.bgColor,
                                    color: config.color,
                                    border: `2px solid ${config.color}`,
                                    padding: '8px 12px',
                                    borderRadius: '8px',
                                    fontWeight: 'bold',
                                    fontSize: '1rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    marginBottom: '8px'
                                  }}
                                  title={reasoning}
                                >
                                  <span style={{fontSize: '1.2rem'}}>{config.icon}</span>
                                  {signal}
                                </div>
                                <div className="confidence" style={{
                                  fontSize: '0.9rem',
                                  color: '#666',
                                  marginBottom: '4px'
                                }}>
                                  Confidence: {confidence.toFixed(1)}%
                                </div>
                                <div className="prediction-reasoning" style={{
                                  fontSize: '0.85rem',
                                  color: '#888',
                                  fontStyle: 'italic',
                                  marginTop: '4px'
                                }}>
                                  {reasoning}
                                </div>
                              </div>
                            )}

                            {item.notes && <div className="stock-notes">📝 {item.notes}</div>}
                          </div>

                          <div className="stock-actions">
                            <button
                              className="btn-remove"
                              onClick={() => handleRemoveStock(item.ticker)}
                              title="Remove from watchlist"
                            >
                              Remove
                            </button>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                ) : (
                  <div className="empty-state">
                    No stocks in this watchlist yet. Add some above!
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="empty-state">
              Select a watchlist to view its stocks
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

WatchlistManager.propTypes = {
  userId: PropTypes.string
};

export default WatchlistManager;
