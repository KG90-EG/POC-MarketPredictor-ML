import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { api, apiClient, fetchWatchlists, createWatchlist, deleteWatchlist, addStockToWatchlist, removeStockFromWatchlist, CURRENT_USER_ID } from '../api';
import ConfirmDialog from './ConfirmDialog';
import './WatchlistManagerV2.css';

/**
 * Modern Watchlist Manager - Simplified & User-Friendly
 *
 * Features:
 * - Card-based design (übersichtlicher)
 * - Delete watchlist with confirmation
 * - Quick add stocks
 * - Live prices & predictions
 * - Compact, mobile-friendly layout
 */
function WatchlistManagerV2({ userId = CURRENT_USER_ID }) {
  const [watchlists, setWatchlists] = useState([]);
  const [selectedWatchlist, setSelectedWatchlist] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWatchlistName, setNewWatchlistName] = useState('');
  const [newStockTicker, setNewStockTicker] = useState('');
  const [stockData, setStockData] = useState({});
  const [loadingStocks, setLoadingStocks] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null); // { id, name }
  const [editingWatchlist, setEditingWatchlist] = useState(null); // { id, name }
  const [editName, setEditName] = useState('');

  useEffect(() => {
    loadWatchlists();
  }, [userId]);

  useEffect(() => {
    if (selectedWatchlist?.items?.length > 0) {
      fetchStockData(selectedWatchlist.items.map(item => item.ticker));
    }
  }, [selectedWatchlist]);

  const loadWatchlists = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchWatchlists(userId);
      const watchlistArray = Array.isArray(data) ? data : [];
      setWatchlists(watchlistArray);

      // Auto-select first watchlist if none selected
      if (!selectedWatchlist && watchlistArray.length > 0) {
        handleSelectWatchlist(watchlistArray[0]);
      }
    } catch (err) {
      setError('Failed to load watchlists');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWatchlist = async (e) => {
    e.preventDefault();
    console.log('Creating watchlist:', newWatchlistName);
    if (!newWatchlistName.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const result = await createWatchlist(userId, {
        name: newWatchlistName,
        description: ''
      });
      console.log('Watchlist created:', result);
      setNewWatchlistName('');
      setShowCreateForm(false);
      await loadWatchlists();
    } catch (err) {
      console.error('Create watchlist error:', err);
      setError(err.response?.data?.detail || 'Failed to create watchlist');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectWatchlist = async (watchlist) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getWatchlist(userId, watchlist.id);
      setSelectedWatchlist(response.data);
    } catch (err) {
      setError('Failed to load watchlist details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteWatchlist = async (watchlistId) => {
    setLoading(true);
    setError(null);
    try {
      await deleteWatchlist(userId, watchlistId);

      // Clear selection if deleted watchlist was selected
      if (selectedWatchlist?.id === watchlistId) {
        setSelectedWatchlist(null);
      }

      await loadWatchlists();
      setDeleteConfirm(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete watchlist');
    } finally {
      setLoading(false);
    }
  };

  const handleEditWatchlist = async (watchlistId) => {
    if (!editName.trim()) return;

    setLoading(true);
    setError(null);
    try {
      await api.updateWatchlist(userId, watchlistId, {
        name: editName,
        description: ''
      });

      setEditingWatchlist(null);
      setEditName('');
      await loadWatchlists();

      // Update selected watchlist if it was edited
      if (selectedWatchlist?.id === watchlistId) {
        const response = await api.getWatchlist(userId, watchlistId);
        setSelectedWatchlist(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update watchlist');
    } finally {
      setLoading(false);
    }
  };

  const startEditing = (watchlist) => {
    setEditingWatchlist({ id: watchlist.id, name: watchlist.name });
    setEditName(watchlist.name);
  };

  const cancelEditing = () => {
    setEditingWatchlist(null);
    setEditName('');
  };

  const handleAddStock = async (e) => {
    e.preventDefault();
    if (!selectedWatchlist || !newStockTicker.trim()) return;

    setLoading(true);
    setError(null);
    try {
      await addStockToWatchlist(userId, selectedWatchlist.id, {
        ticker: newStockTicker.toUpperCase(),
        notes: '',
        asset_type: 'stock'
      });

      setNewStockTicker('');

      // Refresh watchlist
      const response = await api.getWatchlist(userId, selectedWatchlist.id);
      setSelectedWatchlist(response.data);
      await loadWatchlists();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add stock');
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

      // Refresh watchlist
      const response = await api.getWatchlist(userId, selectedWatchlist.id);
      setSelectedWatchlist(response.data);
      await loadWatchlists();
    } catch (err) {
      setError('Failed to remove stock');
    } finally {
      setLoading(false);
    }
  };

  const fetchStockData = async (tickers) => {
    if (tickers.length === 0) return;

    setLoadingStocks(true);
    try {
      const dataPromises = tickers.map(async ticker => {
        try {
          const [infoRes, predRes] = await Promise.all([
            apiClient.get(`/ticker_info/${ticker}`),
            apiClient.get(`/predict_ticker/${ticker}`)
          ]);
          return {
            ticker,
            info: infoRes.data,
            prediction: predRes.data
          };
        } catch (err) {
          console.error(`Failed to fetch data for ${ticker}:`, err);
          return { ticker, info: null, prediction: null };
        }
      });

      const results = await Promise.all(dataPromises);
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
    <div className="watchlist-manager-v2">
      {/* Header */}
      <div className="wl-header">
        <div>
          <h2>⭐ My Watchlists</h2>
          <p className="subtitle">Track your favorite stocks & crypto</p>
        </div>
        <button
          className="btn-primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
          disabled={loading}
        >
          {showCreateForm ? '✕ Cancel' : '+ New Watchlist'}
        </button>
      </div>

      {error && (
        <div className="alert-error">
          ⚠️ {error}
        </div>
      )}

      {/* Create Form */}
      {showCreateForm && (
        <form className="create-form" onSubmit={handleCreateWatchlist}>
          <input
            type="text"
            placeholder="Watchlist name (max 50 characters)"
            value={newWatchlistName}
            onChange={(e) => setNewWatchlistName(e.target.value.slice(0, 50))}
            autoFocus
            required
            maxLength={50}
          />
          <button type="submit" disabled={loading}>
            Create
          </button>
        </form>
      )}

      {/* Watchlist Grid */}
      {loading && (!watchlists || watchlists.length === 0) ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading watchlists...</p>
        </div>
      ) : (!watchlists || watchlists.length === 0) ? (
        <div className="empty-state">
          <span className="empty-icon">📊</span>
          <h3>No watchlists yet</h3>
          <p>Create your first watchlist to start tracking stocks</p>
        </div>
      ) : (
        <div className="watchlist-grid">
          {(watchlists || []).map((watchlist) => (
            <div
              key={watchlist.id}
              className={`watchlist-card ${selectedWatchlist?.id === watchlist.id ? 'selected' : ''}`}
              onClick={() => handleSelectWatchlist(watchlist)}
            >
              <div className="card-header">
                {editingWatchlist?.id === watchlist.id ? (
                  <form
                    className="edit-form-inline"
                    onSubmit={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleEditWatchlist(watchlist.id);
                    }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value.slice(0, 50))}
                      maxLength={50}
                      autoFocus
                      onClick={(e) => e.stopPropagation()}
                    />
                    <button type="submit" className="btn-save-small" title="Save">✓</button>
                    <button
                      type="button"
                      className="btn-cancel-small"
                      onClick={(e) => {
                        e.stopPropagation();
                        cancelEditing();
                      }}
                      title="Cancel"
                    >
                      ✕
                    </button>
                  </form>
                ) : (
                  <>
                    <h3>{watchlist.name}</h3>
                    <div className="card-actions">
                      <button
                        className="btn-edit-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          startEditing(watchlist);
                        }}
                        title="Edit name"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-delete-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteConfirm({ id: watchlist.id, name: watchlist.name });
                        }}
                        title="Delete watchlist"
                      >
                        🗑️
                      </button>
                    </div>
                  </>
                )}
              </div>
              <div className="card-stats">
                <span className="stat">
                  <span className="stat-value">{watchlist.item_count || 0}</span>
                  <span className="stat-label">stocks</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Selected Watchlist Details */}
      {selectedWatchlist && (
        <div className="watchlist-details-section">
          <div className="section-header">
            <h3>📈 {selectedWatchlist.name}</h3>
            <span className="item-count">{selectedWatchlist.items?.length || 0} items</span>
          </div>

          {/* Add Stock Form */}
          <form className="add-stock-form-compact" onSubmit={handleAddStock}>
            <input
              type="text"
              placeholder="Add stock (e.g., AAPL, TSLA, MSFT)"
              value={newStockTicker}
              onChange={(e) => setNewStockTicker(e.target.value)}
              required
            />
            <button type="submit" disabled={loading}>
              + Add
            </button>
          </form>

          {/* Stocks List */}
          {loadingStocks && (
            <div className="loading-stocks">Loading prices...</div>
          )}

          {selectedWatchlist.items?.length > 0 ? (
            <div className="stocks-grid">
              {selectedWatchlist.items.map((item) => {
                const data = stockData[item.ticker];
                const info = data?.info;
                const prediction = data?.prediction;
                const price = info?.price;
                const change = info?.change;
                const changePercent = (change && price) ? (change / (price - change)) * 100 : 0;

                // Prediction signal
                const prob = prediction?.prob || 0.5;
                const signal = prob >= 0.65 ? 'BUY' : prob >= 0.55 ? 'WEAK BUY' : prob >= 0.45 ? 'HOLD' : prob >= 0.35 ? 'WEAK SELL' : 'SELL';
                const signalColor = prob >= 0.65 ? '#10b981' : prob >= 0.55 ? '#84cc16' : prob >= 0.45 ? '#f59e0b' : prob >= 0.35 ? '#f97316' : '#ef4444';

                return (
                  <div key={item.id} className="stock-card">
                    <div className="stock-card-header">
                      <div>
                        <h4>{item.ticker}</h4>
                        {info?.name && <p className="company-name">{info.name}</p>}
                      </div>
                      <button
                        className="btn-remove-icon"
                        onClick={() => handleRemoveStock(item.ticker)}
                        title="Remove"
                      >
                        ✕
                      </button>
                    </div>

                    {price && (
                      <div className="price-section">
                        <div className="price-main">${price.toFixed(2)}</div>
                        <div className={`price-change ${changePercent >= 0 ? 'positive' : 'negative'}`}>
                          {changePercent >= 0 ? '↑' : '↓'} {Math.abs(changePercent).toFixed(2)}%
                        </div>
                      </div>
                    )}

                    {prediction && (
                      <div className="prediction-section">
                        <div
                          className="signal-badge"
                          style={{ backgroundColor: signalColor }}
                        >
                          {signal}
                        </div>
                        <div className="confidence-bar">
                          <div
                            className="confidence-fill"
                            style={{
                              width: `${prob * 100}%`,
                              backgroundColor: signalColor
                            }}
                          />
                        </div>
                        <div className="confidence-text">{(prob * 100).toFixed(0)}% confidence</div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="empty-state-small">
              <p>No stocks yet. Add one above to get started!</p>
            </div>
          )}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!deleteConfirm}
        title="Delete Watchlist?"
        message={deleteConfirm ? `Are you sure you want to delete "${deleteConfirm.name}"? This action cannot be undone.` : ''}
        confirmText="Delete"
        cancelText="Cancel"
        confirmType="danger"
        onConfirm={() => {
          if (deleteConfirm) {
            handleDeleteWatchlist(deleteConfirm.id);
          }
        }}
        onCancel={() => setDeleteConfirm(null)}
      />
    </div>
  );
}

WatchlistManagerV2.propTypes = {
  userId: PropTypes.string
};

export default WatchlistManagerV2;
