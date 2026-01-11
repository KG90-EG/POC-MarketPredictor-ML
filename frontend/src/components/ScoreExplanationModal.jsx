import React from 'react';

const ScoreExplanationModal = ({ ticker, scoreData, onClose }) => {
  if (!scoreData) return null;

  const {
    composite_score,
    score_breakdown,
    top_factors,
    risk_factors,
    signal,
    allocation_limit,
    llm_context
  } = scoreData;

  // Calculate percentage contributions
  const technical = score_breakdown?.technical || 0;
  const ml = score_breakdown?.ml || 0;
  const momentum = score_breakdown?.momentum || 0;
  const regime = score_breakdown?.regime || 0;
  const llm_adjustment = score_breakdown?.llm_adjustment || 0;

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 65) return '#2563eb';
    if (score >= 45) return '#f59e0b';
    if (score >= 35) return '#f97316';
    return '#ef4444';
  };

  const getSignalClass = (signal) => {
    if (!signal) return 'signal-hold';
    return `signal-${signal.toLowerCase().replace(/\s+/g, '_')}`;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content score-explanation" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2>
            <span className="ticker-symbol">{ticker}</span> Score Breakdown
          </h2>
          <button className="modal-close" onClick={onClose} aria-label="Close modal">
            ✕
          </button>
        </div>

        {/* Overall Score */}
        <div className="overall-score-section">
          <div className="score-circle-large" style={{ borderColor: getScoreColor(composite_score) }}>
            <div className="score-value" style={{ color: getScoreColor(composite_score) }}>
              {composite_score?.toFixed(0) || 'N/A'}
            </div>
            <div className="score-label">/ 100</div>
          </div>
          <div className="score-signal">
            <span className={`signal-badge ${getSignalClass(signal)}`}>
              {signal || 'HOLD'}
            </span>
          </div>
          <div className="allocation-recommendation">
            <strong>Max Allocation:</strong> {allocation_limit || 10}%
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="breakdown-section">
          <h3>Component Scores</h3>

          <div className="breakdown-item">
            <div className="breakdown-header">
              <span className="breakdown-label">
                📊 Technical Signals
                <span className="breakdown-weight">(40% weight)</span>
              </span>
              <span className="breakdown-score">{technical?.toFixed(0)}/100</span>
            </div>
            <div className="breakdown-bar">
              <div
                className="breakdown-fill technical"
                style={{ width: `${technical}%` }}
              />
            </div>
          </div>

          <div className="breakdown-item">
            <div className="breakdown-header">
              <span className="breakdown-label">
                🤖 ML Prediction
                <span className="breakdown-weight">(30% weight)</span>
              </span>
              <span className="breakdown-score">{ml?.toFixed(0)}/100</span>
            </div>
            <div className="breakdown-bar">
              <div
                className="breakdown-fill ml"
                style={{ width: `${ml}%` }}
              />
            </div>
          </div>

          <div className="breakdown-item">
            <div className="breakdown-header">
              <span className="breakdown-label">
                📈 Momentum
                <span className="breakdown-weight">(20% weight)</span>
              </span>
              <span className="breakdown-score">{momentum?.toFixed(0)}/100</span>
            </div>
            <div className="breakdown-bar">
              <div
                className="breakdown-fill momentum"
                style={{ width: `${momentum}%` }}
              />
            </div>
          </div>

          <div className="breakdown-item">
            <div className="breakdown-header">
              <span className="breakdown-label">
                🌍 Market Regime
                <span className="breakdown-weight">(10% weight)</span>
              </span>
              <span className="breakdown-score">{regime?.toFixed(0)}/100</span>
            </div>
            <div className="breakdown-bar">
              <div
                className="breakdown-fill regime"
                style={{ width: `${regime}%` }}
              />
            </div>
          </div>

          {llm_adjustment !== 0 && (
            <div className="breakdown-item">
              <div className="breakdown-header">
                <span className="breakdown-label">
                  📰 LLM Context Adjustment
                  <span className="breakdown-weight">(±5% max)</span>
                </span>
                <span className="breakdown-score" style={{ color: llm_adjustment > 0 ? '#10b981' : '#ef4444' }}>
                  {llm_adjustment > 0 ? '+' : ''}{llm_adjustment?.toFixed(2)}
                </span>
              </div>
              <div className="breakdown-bar">
                <div
                  className={`breakdown-fill ${llm_adjustment > 0 ? 'llm-positive' : 'llm-negative'}`}
                  style={{
                    width: `${Math.abs(llm_adjustment) * 20}%`,
                    marginLeft: llm_adjustment < 0 ? `${100 - Math.abs(llm_adjustment) * 20}%` : '0'
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* LLM Context Summary */}
        {llm_context && (
          <div className="llm-context-section">
            <h3>📰 Market Context</h3>
            <p className="llm-summary">{llm_context}</p>
          </div>
        )}

        {/* Top Positive Factors */}
        {top_factors && top_factors.length > 0 && (
          <div className="factors-section positive">
            <h3>✓ Positive Factors</h3>
            <ul className="factors-list">
              {top_factors.map((factor, idx) => (
                <li key={idx} className="factor-item positive">
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Risk Factors */}
        {risk_factors && risk_factors.length > 0 && (
          <div className="factors-section negative">
            <h3>⚠ Risk Factors</h3>
            <ul className="factors-list">
              {risk_factors.map((factor, idx) => (
                <li key={idx} className="factor-item negative">
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Calculation Formula */}
        <div className="formula-section">
          <h3>Score Formula</h3>
          <div className="formula">
            <code>
              Final Score = (Technical × 0.40) + (ML × 0.30) + (Momentum × 0.20) + (Regime × 0.10){llm_adjustment !== 0 ? ' + LLM Adjustment' : ''}
            </code>
          </div>
          <div className="formula-result">
            <code>
              = ({technical?.toFixed(0)} × 0.40) + ({ml?.toFixed(0)} × 0.30) +
              ({momentum?.toFixed(0)} × 0.20) + ({regime?.toFixed(0)} × 0.10)
              {llm_adjustment !== 0 ? ` + ${llm_adjustment > 0 ? '+' : ''}${llm_adjustment?.toFixed(2)}` : ''} = {composite_score?.toFixed(0)}
            </code>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ScoreExplanationModal;
