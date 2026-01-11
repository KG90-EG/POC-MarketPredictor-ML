import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import "./Onboarding.css";

const Onboarding = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Check if user has completed onboarding before
    const hasCompletedOnboarding = localStorage.getItem("onboarding_completed");
    if (!hasCompletedOnboarding) {
      setIsVisible(true);
    }
  }, []);

  const steps = [
    {
      title: "👋 Welcome to Market Predictor!",
      content: "AI-powered stock & crypto analysis to help you make smarter investment decisions.",
      image: "📊",
      cta: "Get Started",
    },
    {
      title: "🎯 Find Buy Opportunities",
      content:
        "Our AI analyzes thousands of stocks and crypto assets to find the best opportunities based on momentum, volatility, and market trends.",
      image: "🔍",
      cta: "Next",
      highlight: "market-selector",
    },
    {
      title: "📈 Track Your Watchlist",
      content:
        "Add your favorite stocks and cryptos to your watchlist. Set price alerts and track AI predictions in one place.",
      image: "⭐",
      cta: "Next",
      highlight: "watchlist",
    },
    {
      title: "📊 Analyze Details",
      content:
        "Click on any stock or crypto to see detailed analysis: price charts, news, technical indicators, and AI confidence scores.",
      image: "🔬",
      cta: "Next",
      highlight: "rankings",
    },
    {
      title: "✨ You're All Set!",
      content:
        "Start exploring buy opportunities, build your watchlist, and let AI help guide your investment decisions.",
      image: "🚀",
      cta: "Start Exploring",
    },
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    localStorage.setItem("onboarding_completed", "true");
    setIsVisible(false);
    if (onComplete) {
      onComplete();
    }
  };

  const handleDotClick = (index) => {
    setCurrentStep(index);
  };

  if (!isVisible) {
    return null;
  }

  const step = steps[currentStep];

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-modal">
        <button className="onboarding-skip" onClick={handleSkip} aria-label="Skip onboarding">
          Skip
        </button>

        <div className="onboarding-content">
          <div className="onboarding-image">
            <span className="onboarding-emoji">{step.image}</span>
          </div>

          <h2 className="onboarding-title">{step.title}</h2>
          <p className="onboarding-description">{step.content}</p>

          <div className="onboarding-progress">
            {steps.map((_, index) => (
              <button
                key={index}
                className={`onboarding-dot ${index === currentStep ? "active" : ""} ${index < currentStep ? "completed" : ""}`}
                onClick={() => handleDotClick(index)}
                aria-label={`Go to step ${index + 1}`}
              />
            ))}
          </div>

          <div className="onboarding-actions">
            {currentStep > 0 && (
              <button
                className="onboarding-btn onboarding-btn-secondary"
                onClick={() => setCurrentStep(currentStep - 1)}
              >
                Back
              </button>
            )}
            <button className="onboarding-btn onboarding-btn-primary" onClick={handleNext}>
              {step.cta}
            </button>
          </div>

          <div className="onboarding-step-counter">
            Step {currentStep + 1} of {steps.length}
          </div>
        </div>
      </div>
    </div>
  );
};

Onboarding.propTypes = {
  onComplete: PropTypes.func,
};

export default Onboarding;
