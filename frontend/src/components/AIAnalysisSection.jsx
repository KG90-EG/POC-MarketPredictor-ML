import React from 'react'
import PropTypes from 'prop-types'

function AIAnalysisSection({
  userContext,
  onContextChange,
  onAnalyze,
  analyzing,
  analysis,
}) {
  return (
    <>
      {/* AI Analysis Section */}
      <section className="analysis-section" role="region" aria-label="AI analysis context input">
        <label>
          <strong>🤖 Optional context for AI analysis</strong>
          <textarea
            value={userContext}
            onChange={(e) => onContextChange(e.target.value)}
            placeholder="e.g., I'm interested in tech stocks with growth potential, looking for long-term investments..."
            rows={3}
            aria-label="Enter context for AI analysis"
          />
        </label>
        <button
          onClick={onAnalyze}
          disabled={analyzing}
          aria-label="Request AI analysis and recommendations"
        >
          {analyzing ? (
            <>
              <span className="spinner"></span>
              Analyzing...
            </>
          ) : (
            '✨ Get AI Recommendations'
          )}
        </button>
      </section>

      {/* AI Analysis Result */}
      {analysis && (
        <section className="analysis-result" role="region" aria-label="AI analysis results">
          <h3>💡 AI Analysis & Recommendations</h3>
          <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{analysis}</p>
        </section>
      )}
    </>
  )
}

AIAnalysisSection.propTypes = {
  userContext: PropTypes.string.isRequired,
  onContextChange: PropTypes.func.isRequired,
  onAnalyze: PropTypes.func.isRequired,
  analyzing: PropTypes.bool.isRequired,
  analysis: PropTypes.string,
}

export default AIAnalysisSection
