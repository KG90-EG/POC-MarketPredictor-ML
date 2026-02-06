import { useState, useEffect } from "react";
import "./KeyboardShortcuts.css";

/**
 * Keyboard Shortcuts Overlay
 * Shows available keyboard shortcuts when user presses "?"
 * Accessibility: Helps keyboard users discover navigation options
 */
function KeyboardShortcuts() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Show shortcuts with "?" or "Shift+/"
      if (e.key === "?" || (e.shiftKey && e.key === "/")) {
        e.preventDefault();
        setIsVisible(true);
      }

      // Hide with Escape
      if (e.key === "Escape" && isVisible) {
        setIsVisible(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isVisible]);

  if (!isVisible) return null;

  const shortcuts = [
    {
      category: "Navigation",
      items: [
        { keys: ["Tab"], description: "Move to next element" },
        { keys: ["Shift", "Tab"], description: "Move to previous element" },
        { keys: ["Enter"], description: "Activate focused element" },
        { keys: ["Esc"], description: "Close dialogs or cancel" },
        { keys: ["0"], description: "Skip to main content" },
      ],
    },
    {
      category: "Views",
      items: [
        { keys: ["1"], description: "Go to Buy Opportunities" },
        { keys: ["2"], description: "Go to Stock Rankings" },
        { keys: ["3"], description: "Go to Crypto Portfolio" },
        { keys: ["4"], description: "Go to Watchlist" },
        { keys: ["5"], description: "Go to Simulations" },
      ],
    },
    {
      category: "Actions",
      items: [
        { keys: ["/"], description: "Focus search" },
        { keys: ["?"], description: "Show this help" },
        { keys: ["r"], description: "Refresh data" },
        { keys: ["d"], description: "Toggle dark mode" },
      ],
    },
  ];

  return (
    <div
      className="keyboard-shortcuts-overlay"
      onClick={() => setIsVisible(false)}
      role="dialog"
      aria-modal="true"
      aria-labelledby="shortcuts-title"
    >
      <div className="keyboard-shortcuts-panel" onClick={(e) => e.stopPropagation()}>
        <div className="keyboard-shortcuts-header">
          <h2 id="shortcuts-title">⌨️ Keyboard Shortcuts</h2>
          <button
            className="keyboard-shortcuts-close"
            onClick={() => setIsVisible(false)}
            aria-label="Close keyboard shortcuts"
          >
            ✕
          </button>
        </div>

        <div className="keyboard-shortcuts-content">
          {shortcuts.map((section, idx) => (
            <div key={idx} className="shortcuts-section">
              <h3 className="shortcuts-category">{section.category}</h3>
              <div className="shortcuts-list">
                {section.items.map((shortcut, i) => (
                  <div key={i} className="shortcut-item">
                    <div className="shortcut-keys">
                      {shortcut.keys.map((key, j) => (
                        <span key={j}>
                          <kbd className="shortcut-key">{key}</kbd>
                          {j < shortcut.keys.length - 1 && <span className="shortcut-plus">+</span>}
                        </span>
                      ))}
                    </div>
                    <div className="shortcut-description">{shortcut.description}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="keyboard-shortcuts-footer">
          <p>
            Press <kbd>?</kbd> to show/hide this panel • Press <kbd>Esc</kbd> to close
          </p>
        </div>
      </div>
    </div>
  );
}

export default KeyboardShortcuts;
