import { useState, useEffect, createContext, useContext } from "react";

/**
 * A/B Testing Infrastructure
 *
 * Allows running controlled experiments to test different UI variations.
 * Features:
 * - Multi-variant testing (A/B/n)
 * - Persistent variant assignment
 * - Conversion tracking
 * - Statistical significance calculation
 */

// Create context for A/B testing
const ABTestContext = createContext({
  getVariant: () => "A",
  trackConversion: () => {},
  trackEvent: () => {},
  experiments: {},
});

export const useABTest = () => useContext(ABTestContext);

/**
 * ABTestProvider
 * Manages all A/B tests across the application
 */
export const ABTestProvider = ({ children, experiments = {} }) => {
  const [userVariants, setUserVariants] = useState({});
  const [userId, setUserId] = useState(null);

  // Initialize user ID and load saved variants
  useEffect(() => {
    // Get or create user ID
    let id = localStorage.getItem("ab_user_id");
    if (!id) {
      id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem("ab_user_id", id);
    }
    setUserId(id);

    // Load saved variant assignments
    const savedVariants = JSON.parse(localStorage.getItem("ab_variants") || "{}");
    setUserVariants(savedVariants);
  }, []);

  // Assign user to a variant for a specific experiment
  const getVariant = (experimentName) => {
    const experiment = experiments[experimentName];
    if (!experiment) {
      console.warn(`[ABTest] Experiment "${experimentName}" not found`);
      return "A";
    }

    // Return existing assignment if available
    if (userVariants[experimentName]) {
      return userVariants[experimentName];
    }

    // Assign new variant based on weights
    const variants = experiment.variants || ["A", "B"];
    const weights = experiment.weights || variants.map(() => 1 / variants.length);

    const random = Math.random();
    let cumulativeWeight = 0;
    let assignedVariant = variants[0];

    for (let i = 0; i < variants.length; i++) {
      cumulativeWeight += weights[i];
      if (random <= cumulativeWeight) {
        assignedVariant = variants[i];
        break;
      }
    }

    // Save assignment
    const newVariants = { ...userVariants, [experimentName]: assignedVariant };
    setUserVariants(newVariants);
    localStorage.setItem("ab_variants", JSON.stringify(newVariants));

    // Track assignment
    trackAssignment(experimentName, assignedVariant);

    return assignedVariant;
  };

  // Track when a user is assigned to a variant
  const trackAssignment = (experimentName, variant) => {
    const assignmentData = {
      userId,
      experiment: experimentName,
      variant,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      screenSize: `${window.innerWidth}x${window.innerHeight}`,
    };

    // Store in localStorage
    const assignments = JSON.parse(localStorage.getItem("ab_assignments") || "[]");
    assignments.push(assignmentData);
    localStorage.setItem("ab_assignments", JSON.stringify(assignments));

    // Send to backend
    sendToBackend("/api/ab-test/assignment", assignmentData);

    console.log("[ABTest] User assigned:", assignmentData);
  };

  // Track conversion events
  const trackConversion = (experimentName, conversionType = "default", value = 1) => {
    const variant = userVariants[experimentName];
    if (!variant) {
      console.warn(`[ABTest] No variant assigned for experiment "${experimentName}"`);
      return;
    }

    const conversionData = {
      userId,
      experiment: experimentName,
      variant,
      conversionType,
      value,
      timestamp: Date.now(),
    };

    // Store in localStorage
    const conversions = JSON.parse(localStorage.getItem("ab_conversions") || "[]");
    conversions.push(conversionData);
    localStorage.setItem("ab_conversions", JSON.stringify(conversions));

    // Send to backend
    sendToBackend("/api/ab-test/conversion", conversionData);

    console.log("[ABTest] Conversion tracked:", conversionData);
  };

  // Track custom events
  const trackEvent = (experimentName, eventName, data = {}) => {
    const variant = userVariants[experimentName];
    if (!variant) {
      console.warn(`[ABTest] No variant assigned for experiment "${experimentName}"`);
      return;
    }

    const eventData = {
      userId,
      experiment: experimentName,
      variant,
      eventName,
      data,
      timestamp: Date.now(),
    };

    // Store in localStorage
    const events = JSON.parse(localStorage.getItem("ab_events") || "[]");
    events.push(eventData);
    localStorage.setItem("ab_events", JSON.stringify(events));

    // Send to backend
    sendToBackend("/api/ab-test/event", eventData);

    console.log("[ABTest] Event tracked:", eventData);
  };

  // Send data to backend
  const sendToBackend = async (endpoint, data) => {
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.warn(`[ABTest] Failed to send data to ${endpoint}:`, error);
    }
  };

  const value = {
    getVariant,
    trackConversion,
    trackEvent,
    experiments,
    userId,
    userVariants,
  };

  return <ABTestContext.Provider value={value}>{children}</ABTestContext.Provider>;
};

/**
 * ABTest Component
 * Renders different variants based on A/B test assignment
 */
export const ABTest = ({ name, children }) => {
  const { getVariant } = useABTest();
  const variant = getVariant(name);

  // Find the matching variant component
  const variantComponent = children.find((child) => child.props.variant === variant);

  return variantComponent || children[0] || null;
};

/**
 * Variant Component
 * Wrapper for individual test variants
 */
export const Variant = ({ variant, children }) => {
  return <>{children}</>;
};

/**
 * Calculate statistical significance using Chi-square test
 */
export const calculateSignificance = (variantA, variantB) => {
  const { conversions: convA, impressions: impA } = variantA;
  const { conversions: convB, impressions: impB } = variantB;

  // Calculate conversion rates
  const rateA = convA / impA;
  const rateB = convB / impB;

  // Calculate pooled probability
  const pooledP = (convA + convB) / (impA + impB);

  // Calculate standard error
  const se = Math.sqrt(pooledP * (1 - pooledP) * (1 / impA + 1 / impB));

  // Calculate z-score
  const zScore = (rateA - rateB) / se;

  // Calculate p-value (two-tailed)
  const pValue = 2 * (1 - normalCDF(Math.abs(zScore)));

  // Calculate confidence interval (95%)
  const diff = rateA - rateB;
  const ci = 1.96 * se;

  return {
    variantA: {
      rate: rateA,
      conversions: convA,
      impressions: impA,
    },
    variantB: {
      rate: rateB,
      conversions: convB,
      impressions: impB,
    },
    difference: diff,
    confidenceInterval: {
      lower: diff - ci,
      upper: diff + ci,
    },
    zScore,
    pValue,
    significant: pValue < 0.05,
    confidence: (1 - pValue) * 100,
  };
};

// Helper: Normal CDF approximation
const normalCDF = (x) => {
  const t = 1 / (1 + 0.2316419 * Math.abs(x));
  const d = 0.3989423 * Math.exp((-x * x) / 2);
  const prob =
    d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return x > 0 ? 1 - prob : prob;
};

/**
 * Analyze A/B test results from localStorage
 */
export const analyzeABTestResults = () => {
  const assignments = JSON.parse(localStorage.getItem("ab_assignments") || "[]");
  const conversions = JSON.parse(localStorage.getItem("ab_conversions") || "[]");
  const events = JSON.parse(localStorage.getItem("ab_events") || "[]");

  // Group by experiment
  const experimentResults = {};

  // Count impressions (assignments)
  assignments.forEach((assignment) => {
    const { experiment, variant } = assignment;
    if (!experimentResults[experiment]) {
      experimentResults[experiment] = {};
    }
    if (!experimentResults[experiment][variant]) {
      experimentResults[experiment][variant] = {
        impressions: 0,
        conversions: 0,
        events: {},
      };
    }
    experimentResults[experiment][variant].impressions++;
  });

  // Count conversions
  conversions.forEach((conversion) => {
    const { experiment, variant, conversionType } = conversion;
    if (experimentResults[experiment]?.[variant]) {
      experimentResults[experiment][variant].conversions++;
      if (!experimentResults[experiment][variant].conversionsByType) {
        experimentResults[experiment][variant].conversionsByType = {};
      }
      experimentResults[experiment][variant].conversionsByType[conversionType] =
        (experimentResults[experiment][variant].conversionsByType[conversionType] || 0) + 1;
    }
  });

  // Count events
  events.forEach((event) => {
    const { experiment, variant, eventName } = event;
    if (experimentResults[experiment]?.[variant]) {
      if (!experimentResults[experiment][variant].events[eventName]) {
        experimentResults[experiment][variant].events[eventName] = 0;
      }
      experimentResults[experiment][variant].events[eventName]++;
    }
  });

  // Calculate conversion rates and significance
  Object.keys(experimentResults).forEach((experiment) => {
    const variants = Object.keys(experimentResults[experiment]);

    variants.forEach((variant) => {
      const data = experimentResults[experiment][variant];
      data.conversionRate =
        data.impressions > 0
          ? ((data.conversions / data.impressions) * 100).toFixed(2) + "%"
          : "0%";
    });

    // Calculate significance between first two variants
    if (variants.length >= 2) {
      const variantA = experimentResults[experiment][variants[0]];
      const variantB = experimentResults[experiment][variants[1]];

      if (variantA.impressions > 0 && variantB.impressions > 0) {
        experimentResults[experiment].significance = calculateSignificance(variantA, variantB);
      }
    }
  });

  return experimentResults;
};

export default ABTest;
