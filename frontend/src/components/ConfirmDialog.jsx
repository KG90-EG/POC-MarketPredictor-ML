import { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import './ConfirmDialog.css';

/**
 * Confirmation Dialog Component
 * Shows modal confirmation for destructive actions
 * Implements WCAG 2.1 AA focus management and keyboard navigation
 */
function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmType = 'danger', // 'danger', 'warning', 'primary'
  onConfirm,
  onCancel
}) {
  const dialogRef = useRef(null);
  const confirmBtnRef = useRef(null);
  const previousActiveElement = useRef(null);

  useEffect(() => {
    if (isOpen) {
      // Store the element that triggered the dialog
      previousActiveElement.current = document.activeElement;

      // Focus the confirm button when dialog opens
      setTimeout(() => {
        confirmBtnRef.current?.focus();
      }, 100);

      // Prevent body scroll
      document.body.style.overflow = 'hidden';

      // Trap focus inside dialog
      const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
          onCancel();
        }

        // Tab key handling for focus trap
        if (e.key === 'Tab') {
          const focusableElements = dialogRef.current?.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          );
          const firstElement = focusableElements[0];
          const lastElement = focusableElements[focusableElements.length - 1];

          if (e.shiftKey) {
            // Shift + Tab
            if (document.activeElement === firstElement) {
              e.preventDefault();
              lastElement.focus();
            }
          } else {
            // Tab
            if (document.activeElement === lastElement) {
              e.preventDefault();
              firstElement.focus();
            }
          }
        }
      };

      document.addEventListener('keydown', handleKeyDown);

      return () => {
        document.removeEventListener('keydown', handleKeyDown);
        document.body.style.overflow = '';
        // Restore focus to previous element
        previousActiveElement.current?.focus();
      };
    }
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm();
  };

  const handleCancel = () => {
    onCancel();
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      handleCancel();
    }
  };

  return (
    <div
      className="confirm-dialog-overlay"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
      aria-describedby="dialog-message"
    >
      <div className="confirm-dialog" ref={dialogRef}>
        <div className="confirm-dialog-header">
          <h3 id="dialog-title" className="confirm-dialog-title">
            {title}
          </h3>
          <button
            className="confirm-dialog-close"
            onClick={handleCancel}
            aria-label="Close dialog"
            type="button"
          >
            ✕
          </button>
        </div>

        <div className="confirm-dialog-body">
          <p id="dialog-message" className="confirm-dialog-message">
            {message}
          </p>
        </div>

        <div className="confirm-dialog-footer">
          <button
            className="confirm-dialog-btn confirm-dialog-btn-cancel"
            onClick={handleCancel}
            type="button"
          >
            {cancelText}
          </button>
          <button
            ref={confirmBtnRef}
            className={`confirm-dialog-btn confirm-dialog-btn-${confirmType}`}
            onClick={handleConfirm}
            type="button"
            autoFocus
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

ConfirmDialog.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  title: PropTypes.string.isRequired,
  message: PropTypes.string.isRequired,
  confirmText: PropTypes.string,
  cancelText: PropTypes.string,
  confirmType: PropTypes.oneOf(['danger', 'warning', 'primary']),
  onConfirm: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired
};

export default ConfirmDialog;
