import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { fetchWatchlists, createWatchlist, deleteWatchlist, addStockToWatchlist, removeStockFromWatchlist } from '../api';
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

  useEffect(() => {
    loadWatchlists();
  }, [userId]);

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

  const handleAddStock = async (e) => {
    e.preventDefault();
    if (!selectedWatchlist || !newStockTicker.trim()) return;

    setLoading(true);
    setError(null);
    try {
      await addStockToWatchlist(userId, selectedWatchlist.id, {
        ticker: newStockTicker.toUpperCase(),
        notes: newStockNotes
      });
      setNewStockTicker('');
      setNewStockNotes('');
      await loadWatchlists();
      // Refresh selected watchlist
      const updatedWatchlist = watchlists.find(w => w.id === selectedWatchlist.id);
      setSelectedWatchlist(updatedWatchlist);
    } catch (err) {
      setError('Failed to add stock');
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
      await loadWatchlists();
      // Refresh selected watchlist
      const updatedWatchlist = watchlists.find(w => w.id === selectedWatchlist.id);
      setSelectedWatchlist(updatedWatchlist);
    } catch (err) {
      setError('Failed to remove stock');
      console.error(err);
    } finally {
      setLoading(false);
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
                    onClick={() => setSelectedWatchlist(watchlist)}
                  >
                    <span className="watchlist-name">{watchlist.name}</span>
                    <span className="watchlist-count">{watchlist.item_count || 0} stocks</span>
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
                <input
                  type="text"
                  placeholder="Stock ticker (e.g., AAPL)"
                  value={newStockTicker}
                  onChange={(e) => setNewStockTicker(e.target.value)}
                  required
                />
                <input
                  type="text"
                  placeholder="Notes (optional)"
                  value={newStockNotes}
                  onChange={(e) => setNewStockNotes(e.target.value)}
                />
                <button type="submit" disabled={loading}>
                  Add Stock
                </button>
              </form>

              <div className="stocks-list">
                {selectedWatchlist.items?.length > 0 ? (
                  <ul>
                    {selectedWatchlist.items.map((item) => (
                      <li key={item.id} className="stock-item">
                        <div className="stock-info">
                          <span className="stock-ticker">{item.ticker}</span>
                          {item.notes && <span className="stock-notes">{item.notes}</span>}
                          <span className="stock-date">
                            Added {new Date(item.added_at).toLocaleDateString()}
                          </span>
                        </div>
                        <button
                          className="btn-remove"
                          onClick={() => handleRemoveStock(item.ticker)}
                          title="Remove from watchlist"
                        >
                          Remove
                        </button>
                      </li>
                    ))}
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
