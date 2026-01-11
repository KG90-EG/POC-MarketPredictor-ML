import PropTypes from "prop-types";
import "./OnboardingResetBtn.css";

const OnboardingResetBtn = ({ onReset }) => {
  const handleReset = () => {
    localStorage.removeItem("onboarding_completed");
    if (onReset) {
      onReset();
    }
    // Reload page to trigger onboarding again
    window.location.reload();
  };

  // Only show in development mode
  if (import.meta.env.PROD) {
    return null;
  }

  return (
    <button
      className="onboarding-reset-btn"
      onClick={handleReset}
      title="Reset onboarding (Dev only)"
      aria-label="Reset onboarding tutorial"
    >
      🔄 Reset Tutorial
    </button>
  );
};

OnboardingResetBtn.propTypes = {
  onReset: PropTypes.func,
};

export default OnboardingResetBtn;
