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

    // If empty, show popular items based on asset type
    if (!value.trim()) {
      if (assetType === 'crypto') {
        setFilteredStocks(popularCryptos.slice(0, 10).map(c => ({ ticker: c.id, name: `${c.name} (${c.symbol})` })));
      } else {
        setFilteredStocks(popularStocks.slice(0, 10));
      }
      setShowDropdown(true);
      return;
    }

    // Search dynamically from API for better results
    try {
      const endpoint = assetType === 'crypto' ? '/search_cryptos' : '/search_stocks';
      const response = await apiClient.get(`${endpoint}?query=${encodeURIComponent(value)}&limit=10`);

      if (assetType === 'crypto') {
        const cryptos = response.data.cryptos || [];
        setFilteredStocks(cryptos.map(c => ({ ticker: c.id, name: `${c.name} (${c.symbol})` })));
      } else {
        setFilteredStocks(response.data.stocks || []);
      }
      setShowDropdown(true);
    } catch (err) {
      console.error('Search failed:', err);
      // Fallback to client-side filtering
      const searchTerm = value.toLowerCase();
      const filtered = popularStocks.filter(stock =>
        stock.ticker.toLowerCase().includes(searchTerm) ||
        stock.name.toLowerCase().includes(searchTerm)
      );
      setFilteredStocks(filtered.slice(0, 10));
      setShowDropdown(true);
    }
  };

  const handleStockSelect = (stock) => {
    setNewStockTicker(stock.ticker);
    setNewStockNotes(stock.name);
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
            // For crypto, fetch from crypto details endpoint
            const detailsRes = await apiClient.get(`/crypto/details/${item.ticker}`);
            return {
              ticker: item.ticker,
              info: {
                name: detailsRes.data.name,
                price: detailsRes.data.current_price,
                change: detailsRes.data.price_change_24h,
                volume: detailsRes.data.total_volume,
              },
              prediction: {
                probability: detailsRes.data.momentum_score ? (detailsRes.data.momentum_score + 1) / 2 : 0.5,
                momentum_score: detailsRes.data.momentum_score
              }
            };
          } else {
            // For stocks, use existing endpoints
            const [infoRes, predRes] = await Promise.all([
              api.getTickerInfo(item.ticker),
              api.predictTicker(item.ticker)
            ]);

            return {
              ticker: item.ticker,
              info: infoRes.data,
              prediction: predRes.data
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
                <div className="asset-type-toggle">
                  <button
                    type="button"
                    className={assetType === 'stock' ? 'active' : ''}
                    onClick={() => {
                      setAssetType('stock');
                      setNewStockTicker('');
                      setFilteredStocks([]);
                    }}
                  >
                    📈 Stocks
                  </button>
                  <button
                    type="button"
                    className={assetType === 'crypto' ? 'active' : ''}
                    onClick={() => {
                      setAssetType('crypto');
                      setNewStockTicker('');
                      setFilteredStocks([]);
                    }}
                  >
                    ₿ Crypto
                  </button>
                </div>
                <div className="form-inputs">
                  <div className="stock-input-container">
                    <input
                      type="text"
                      placeholder={assetType === 'stock' ? "Search stocks (e.g., Apple, AAPL)" : "Search crypto (e.g., Bitcoin, BTC)"}
                      value={newStockTicker}
                      onChange={(e) => handleAssetInputChange(e.target.value)}
                      onFocus={() => {
                        if (assetType === 'crypto') {
                          setFilteredStocks(popularCryptos.slice(0, 10).map(c => ({ ticker: c.id, name: `${c.name} (${c.symbol})` })));
                        } else {
                          setFilteredStocks(popularStocks.slice(0, 10));
                        }
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
                    Add {assetType === 'stock' ? 'Stock' : 'Crypto'}
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
                      const probability = prediction?.probability || 0;
                      const recommendation = probability > 0.6 ? 'BUY' : probability < 0.4 ? 'SELL' : 'HOLD';
                      const recColor = probability > 0.6 ? '#10b981' : probability < 0.4 ? '#ef4444' : '#f59e0b';

                      // Map backend response to expected fields
                      const price = info?.price;
                      const change = info?.change;
                      const changePercent = (change && price) ? (change / (price - change)) * 100 : 0;
                      const volume = info?.volume;
                      const fiftyTwoWeekHigh = info?.fifty_two_week_high;

                      return (
                        <li key={item.id} className="stock-item enhanced">
                          <div className="stock-main">
                            <div className="stock-header">
                              <span className="stock-ticker">{item.ticker}</span>
                              {info?.name && (
                                <span className="stock-name">{info.name}</span>
                              )}
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
                                <div className="recommendation" style={{backgroundColor: recColor}}>
                                  {recommendation}
                                </div>
                                <div className="confidence">
                                  Confidence: {(probability * 100).toFixed(1)}%
                                </div>
                                <div className="prediction-details">
                                  <span>Momentum: {prediction.momentum_score?.toFixed(2)}</span>
                                  {fiftyTwoWeekHigh && price && (
                                    <span>From 52w High: {((price / fiftyTwoWeekHigh - 1) * 100).toFixed(1)}%</span>
                                  )}
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
