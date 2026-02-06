import PropTypes from "prop-types";
import "./SkeletonLoader.css";

/**
 * Skeleton Loader Components
 * Provides placeholder UI while content is loading
 */

export function SkeletonLine({ width = "100%", height = "16px", style = {} }) {
  return <div className="skeleton skeleton-line" style={{ width, height, ...style }} />;
}

SkeletonLine.propTypes = {
  width: PropTypes.string,
  height: PropTypes.string,
  style: PropTypes.object,
};

export function SkeletonCircle({ size = "40px", style = {} }) {
  return (
    <div className="skeleton skeleton-circle" style={{ width: size, height: size, ...style }} />
  );
}

SkeletonCircle.propTypes = {
  size: PropTypes.string,
  style: PropTypes.object,
};

export function SkeletonCard({ height = "200px" }) {
  return (
    <div className="skeleton-card" style={{ height }}>
      <SkeletonLine width="60%" height="20px" style={{ marginBottom: "12px" }} />
      <SkeletonLine width="100%" height="14px" style={{ marginBottom: "8px" }} />
      <SkeletonLine width="100%" height="14px" style={{ marginBottom: "8px" }} />
      <SkeletonLine width="80%" height="14px" />
    </div>
  );
}

SkeletonCard.propTypes = {
  height: PropTypes.string,
};

export function SkeletonTable({ rows = 5, columns = 8 }) {
  return (
    <div className="skeleton-table">
      {/* Table Header */}
      <div className="skeleton-table-header">
        {Array.from({ length: columns }).map((_, i) => (
          <SkeletonLine
            key={`header-${i}`}
            width={i === 0 ? "80px" : i === 1 ? "150px" : "100px"}
            height="18px"
            style={{ margin: "8px" }}
          />
        ))}
      </div>

      {/* Table Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={`row-${rowIndex}`} className="skeleton-table-row">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <SkeletonLine
              key={`cell-${rowIndex}-${colIndex}`}
              width={colIndex === 0 ? "60px" : colIndex === 1 ? "120px" : "80px"}
              height="14px"
              style={{ margin: "12px 8px" }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

SkeletonTable.propTypes = {
  rows: PropTypes.number,
  columns: PropTypes.number,
};

export function SkeletonCryptoCard() {
  return (
    <div className="skeleton-crypto-card">
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "12px" }}>
        <SkeletonCircle size="48px" />
        <div style={{ flex: 1 }}>
          <SkeletonLine width="120px" height="18px" style={{ marginBottom: "6px" }} />
          <SkeletonLine width="80px" height="14px" />
        </div>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: "16px" }}>
        <SkeletonLine width="60px" height="16px" />
        <SkeletonLine width="80px" height="16px" />
        <SkeletonLine width="70px" height="16px" />
      </div>
    </div>
  );
}

export function SkeletonStockRow() {
  return (
    <div className="skeleton-stock-row">
      <SkeletonLine width="60px" height="16px" />
      <SkeletonLine width="140px" height="16px" />
      <SkeletonLine width="50px" height="16px" />
      <SkeletonLine width="70px" height="16px" />
      <SkeletonLine width="80px" height="16px" />
      <SkeletonLine width="60px" height="16px" />
      <SkeletonLine width="90px" height="16px" />
      <SkeletonLine width="100px" height="16px" />
    </div>
  );
}

export default SkeletonTable;
