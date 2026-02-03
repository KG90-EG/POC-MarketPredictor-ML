/**
 * SentimentBadge Component
 *
 * Small badge showing sentiment (bullish/bearish/neutral).
 * Color-coded with expand-on-click for headlines.
 */

import React, { useState } from 'react';
import PropTypes from 'prop-types';
import './SentimentBadge.css';

const SENTIMENT_CONFIG = {
  bullish: {
    color: '#22c55e',
    bgColor: '#dcfce7',
    icon: '📈',
    label: 'Bullish',
  },
  bearish: {
    color: '#ef4444',
    bgColor: '#fee2e2',
    icon: '📉',
    label: 'Bearish',
  },
  neutral: {
    color: '#6b7280',
    bgColor: '#f3f4f6',
    icon: '➡️',
    label: 'Neutral',
  },
};

export function SentimentBadge({
  sentiment = 'neutral',
  score,
  headlines = [],
  size = 'medium',
  showLabel = true,
  expandable = true,
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  const config = SENTIMENT_CONFIG[sentiment] || SENTIMENT_CONFIG.neutral;

  const handleClick = () => {
    if (expandable && headlines.length > 0) {
      setIsExpanded(!isExpanded);
    }
  };

  return (
    <div className={`sentiment-wrapper sentiment-wrapper--${size}`}>
      <button
        className={`sentiment-badge sentiment-badge--${sentiment} sentiment-badge--${size}`}
        style={{
          backgroundColor: config.bgColor,
          color: config.color,
          cursor: expandable && headlines.length > 0 ? 'pointer' : 'default',
        }}
        onClick={handleClick}
        title={`${config.label} sentiment${score !== undefined ? ` (${score > 0 ? '+' : ''}${score.toFixed(2)})` : ''}`}
      >
        <span className="sentiment-badge__icon">{config.icon}</span>
        {showLabel && (
          <span className="sentiment-badge__label">{config.label}</span>
        )}
        {score !== undefined && (
          <span className="sentiment-badge__score">
            {score > 0 ? '+' : ''}{score.toFixed(1)}
          </span>
        )}
        {expandable && headlines.length > 0 && (
          <span className={`sentiment-badge__expand ${isExpanded ? 'expanded' : ''}`}>
            ▼
          </span>
        )}
      </button>

      {/* Expanded Headlines */}
      {isExpanded && headlines.length > 0 && (
        <div className="sentiment-headlines">
          <div className="sentiment-headlines__header">
            Recent Headlines
          </div>
          <ul className="sentiment-headlines__list">
            {headlines.slice(0, 5).map((headline, index) => (
              <li key={index} className="sentiment-headlines__item">
                {headline.title || headline}
                {headline.source && (
                  <span className="sentiment-headlines__source">
                    — {headline.source}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

SentimentBadge.propTypes = {
  sentiment: PropTypes.oneOf(['bullish', 'bearish', 'neutral']),
  score: PropTypes.number,
  headlines: PropTypes.arrayOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.shape({
        title: PropTypes.string,
        source: PropTypes.string,
        url: PropTypes.string,
      }),
    ])
  ),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  showLabel: PropTypes.bool,
  expandable: PropTypes.bool,
};

export default SentimentBadge;
