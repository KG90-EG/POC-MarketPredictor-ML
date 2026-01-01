import PropTypes from 'prop-types';
import './EmptyState.css';

/**
 * EmptyState Component
 * Displays a friendly message when there's no data to show
 */
function EmptyState({
  icon = '📊',
  title = 'No data yet',
  description = 'Get started by selecting an option above',
  action = null,
  actionLabel = 'Get Started',
  onAction = null
}) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-description">{description}</p>
      {action && onAction && (
        <button
          className="empty-state-button"
          onClick={onAction}
          aria-label={actionLabel}
        >
          {actionLabel}
        </button>
      )}
      {action && !onAction && action}
    </div>
  );
}

EmptyState.propTypes = {
  icon: PropTypes.string,
  title: PropTypes.string,
  description: PropTypes.string,
  action: PropTypes.node,
  actionLabel: PropTypes.string,
  onAction: PropTypes.func
};

export default EmptyState;
