/**
 * Frontend currency conversion utilities
 * Converts prices from USD to CHF and formats them appropriately
 */

/**
 * Convert price from USD to target currency
 * @param {number} priceUSD - Price in USD
 * @param {string} targetCurrency - Target currency ('USD' or 'CHF')
 * @param {number|null} exchangeRate - USD to CHF exchange rate (required if targetCurrency is 'CHF')
 * @returns {number} Converted price
 */
export function convertPrice(priceUSD, targetCurrency, exchangeRate = null) {
  if (targetCurrency === "USD" || !priceUSD) {
    return priceUSD;
  }

  if (targetCurrency === "CHF") {
    if (!exchangeRate) {
      console.warn("Exchange rate not available, using fallback");
      return priceUSD * 0.85; // Fallback rate
    }
    return priceUSD * exchangeRate;
  }

  return priceUSD;
}

/**
 * Format price with currency symbol
 * @param {number} price - Price to format
 * @param {string} currency - Currency code ('USD' or 'CHF')
 * @returns {string} Formatted price with symbol
 */
export function formatPrice(price, currency = "USD") {
  if (price === null || price === undefined || isNaN(price)) {
    return currency === "USD" ? "$--" : "CHF --";
  }

  const formatted = price.toFixed(2);

  if (currency === "USD") {
    return `$${formatted}`;
  } else if (currency === "CHF") {
    return `CHF ${formatted}`;
  }

  return `${currency} ${formatted}`;
}

/**
 * Convert and format price in one step
 * @param {number} priceUSD - Price in USD
 * @param {string} targetCurrency - Target currency ('USD' or 'CHF')
 * @param {number|null} exchangeRate - USD to CHF exchange rate
 * @returns {string} Formatted price with symbol
 */
export function convertAndFormat(priceUSD, targetCurrency, exchangeRate = null) {
  const converted = convertPrice(priceUSD, targetCurrency, exchangeRate);
  return formatPrice(converted, targetCurrency);
}
