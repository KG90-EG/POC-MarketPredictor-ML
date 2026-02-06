import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import "./FilterBar.css";

/**
 * FilterBar Component
 * Provides filtering and sorting controls for stock tables
 */
function FilterBar({
  stocks,
  onFilterChange,
  showCountryFilter = true,
  showSectorFilter = true,
  showMarketCapFilter = true,
}) {
  const [sortBy, setSortBy] = useState("rank"); // rank, prob, price, volume, market_cap
  const [sortOrder, setSortOrder] = useState("asc"); // asc or desc
  const [selectedCountry, setSelectedCountry] = useState("all");
  const [selectedSector, setSelectedSector] = useState("all");
  const [selectedMarketCap, setSelectedMarketCap] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Extract unique countries and sectors from stocks
  const countries = React.useMemo(() => {
    const uniqueCountries = [...new Set(stocks.map((s) => s.country).filter(Boolean))];
    return uniqueCountries.sort();
  }, [stocks]);

  const sectors = React.useMemo(() => {
    const uniqueSectors = [...new Set(stocks.map((s) => s.sector).filter(Boolean))];
    return uniqueSectors.sort();
  }, [stocks]);

  // Apply filters and sorting
  useEffect(() => {
    let filtered = [...stocks];

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (stock) =>
          (stock.ticker || "").toLowerCase().includes(query) ||
          (stock.name || "").toLowerCase().includes(query) ||
          (stock.sector || "").toLowerCase().includes(query)
      );
    }

    // Country filter
    if (selectedCountry !== "all") {
      filtered = filtered.filter((s) => s.country === selectedCountry);
    }

    // Sector filter
    if (selectedSector !== "all") {
      filtered = filtered.filter((s) => s.sector === selectedSector);
    }

    // Market cap filter
    if (selectedMarketCap !== "all") {
      filtered = filtered.filter((stock) => {
        const marketCap = stock.market_cap || 0;
        switch (selectedMarketCap) {
          case "mega":
            return marketCap >= 200e9; // >= $200B
          case "large":
            return marketCap >= 10e9 && marketCap < 200e9; // $10B - $200B
          case "mid":
            return marketCap >= 2e9 && marketCap < 10e9; // $2B - $10B
          case "small":
            return marketCap < 2e9; // < $2B
          default:
            return true;
        }
      });
    }

    // Sorting
    filtered.sort((a, b) => {
      let aVal, bVal;
      switch (sortBy) {
        case "rank":
          aVal = a.rank || 0;
          bVal = b.rank || 0;
          break;
        case "prob":
          aVal = a.prob || 0;
          bVal = b.prob || 0;
          break;
        case "price":
          aVal = a.price || 0;
          bVal = b.price || 0;
          break;
        case "volume":
          aVal = a.volume || 0;
          bVal = b.volume || 0;
          break;
        case "market_cap":
          aVal = a.market_cap || 0;
          bVal = b.market_cap || 0;
          break;
        case "name":
          aVal = (a.name || a.ticker || "").toLowerCase();
          bVal = (b.name || b.ticker || "").toLowerCase();
          return sortOrder === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        default:
          aVal = 0;
          bVal = 0;
      }

      if (sortOrder === "asc") {
        return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
      } else {
        return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
      }
    });

    onFilterChange(filtered);
  }, [
    stocks,
    sortBy,
    sortOrder,
    selectedCountry,
    selectedSector,
    selectedMarketCap,
    searchQuery,
    onFilterChange,
  ]);

  const handleSortChange = (field) => {
    if (sortBy === field) {
      // Toggle order if same field
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortOrder("desc"); // Default to desc for new field
    }
  };

  const resetFilters = () => {
    setSortBy("rank");
    setSortOrder("asc");
    setSelectedCountry("all");
    setSelectedSector("all");
    setSelectedMarketCap("all");
    setSearchQuery("");
  };

  const activeFiltersCount = [
    selectedCountry !== "all",
    selectedSector !== "all",
    selectedMarketCap !== "all",
    searchQuery.trim() !== "",
  ].filter(Boolean).length;

  return (
    <div className="filter-bar" role="region" aria-label="Stock filters and sorting controls">
      {/* Search Input */}
      <div className="filter-group filter-search">
        <label htmlFor="stock-search" className="filter-label">
          🔍 Search
        </label>
        <input
          id="stock-search"
          type="text"
          placeholder="Search ticker, name, sector..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="filter-input"
          aria-label="Search stocks by ticker, name, or sector"
        />
      </div>

      {/* Sort Controls */}
      <div className="filter-group">
        <label htmlFor="sort-by" className="filter-label">
          🔽 Sort by
        </label>
        <div className="sort-controls">
          <select
            id="sort-by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="filter-select"
            aria-label="Sort stocks by field"
          >
            <option value="rank">Rank</option>
            <option value="prob">Probability</option>
            <option value="name">Name</option>
            <option value="price">Price</option>
            <option value="volume">Volume</option>
            <option value="market_cap">Market Cap</option>
          </select>
          <button
            onClick={() => setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"))}
            className="sort-order-btn"
            aria-label={`Sort order: ${sortOrder === "asc" ? "ascending" : "descending"}`}
            title={sortOrder === "asc" ? "Ascending" : "Descending"}
          >
            {sortOrder === "asc" ? "⬆️" : "⬇️"}
          </button>
        </div>
      </div>

      {/* Country Filter */}
      {showCountryFilter && countries.length > 0 && (
        <div className="filter-group">
          <label htmlFor="country-filter" className="filter-label">
            🌍 Country
          </label>
          <select
            id="country-filter"
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="filter-select"
            aria-label="Filter stocks by country"
          >
            <option value="all">All Countries ({countries.length})</option>
            {countries.map((country) => (
              <option key={country} value={country}>
                {country}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Sector Filter */}
      {showSectorFilter && sectors.length > 0 && (
        <div className="filter-group">
          <label htmlFor="sector-filter" className="filter-label">
            🏭 Sector
          </label>
          <select
            id="sector-filter"
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            className="filter-select"
            aria-label="Filter stocks by sector"
          >
            <option value="all">All Sectors ({sectors.length})</option>
            {sectors.map((sector) => (
              <option key={sector} value={sector}>
                {sector}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Market Cap Filter */}
      {showMarketCapFilter && (
        <div className="filter-group">
          <label htmlFor="marketcap-filter" className="filter-label">
            💰 Market Cap
          </label>
          <select
            id="marketcap-filter"
            value={selectedMarketCap}
            onChange={(e) => setSelectedMarketCap(e.target.value)}
            className="filter-select"
            aria-label="Filter stocks by market capitalization"
          >
            <option value="all">All Sizes</option>
            <option value="mega">Mega Cap (&gt; $200B)</option>
            <option value="large">Large Cap ($10B - $200B)</option>
            <option value="mid">Mid Cap ($2B - $10B)</option>
            <option value="small">Small Cap (&lt; $2B)</option>
          </select>
        </div>
      )}

      {/* Reset Button */}
      {activeFiltersCount > 0 && (
        <div className="filter-group">
          <button
            onClick={resetFilters}
            className="reset-filters-btn"
            aria-label={`Reset ${activeFiltersCount} active filter${activeFiltersCount > 1 ? "s" : ""}`}
          >
            ✕ Reset ({activeFiltersCount})
          </button>
        </div>
      )}
    </div>
  );
}

FilterBar.propTypes = {
  stocks: PropTypes.array.isRequired,
  onFilterChange: PropTypes.func.isRequired,
  showCountryFilter: PropTypes.bool,
  showSectorFilter: PropTypes.bool,
  showMarketCapFilter: PropTypes.bool,
};

export default FilterBar;
