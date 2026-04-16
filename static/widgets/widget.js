/* AtlasPI Widget Shared Logic -- v6.22.0 */

(function () {
  'use strict';

  // Apply theme from query parameter
  const params = new URLSearchParams(window.location.search);
  if (params.get('theme') === 'light') {
    document.documentElement.classList.add('theme-light');
  }

  // Determine API base URL (same origin)
  const API_BASE = window.location.origin;

  /**
   * Format year for display, handling BCE dates.
   * @param {number} year
   * @returns {string}
   */
  function formatYear(year) {
    if (year == null) return '';
    if (year < 0) return Math.abs(year) + ' BCE';
    if (year === 0) return '1 BCE';
    return year + ' CE';
  }

  /**
   * Format year range.
   * @param {number} yearStart
   * @param {number|null} yearEnd
   * @returns {string}
   */
  function formatYearRange(yearStart, yearEnd) {
    if (yearEnd != null && yearEnd !== yearStart) {
      return formatYear(yearStart) + ' \u2013 ' + formatYear(yearEnd);
    }
    return formatYear(yearStart);
  }

  /**
   * Get confidence level label and class.
   * @param {number} score 0.0-1.0
   * @returns {{label: string, cls: string}}
   */
  function confidenceLevel(score) {
    if (score >= 0.8) return { label: 'High (' + (score * 100).toFixed(0) + '%)', cls: 'high' };
    if (score >= 0.5) return { label: 'Medium (' + (score * 100).toFixed(0) + '%)', cls: 'medium' };
    return { label: 'Low (' + (score * 100).toFixed(0) + '%)', cls: 'low' };
  }

  /**
   * Fetch JSON from API with error handling.
   * @param {string} path - API path (e.g., '/v1/entities/1')
   * @returns {Promise<any>}
   */
  async function apiFetch(path) {
    const url = API_BASE + path;
    const resp = await fetch(url, {
      headers: { 'Accept': 'application/json' }
    });
    if (!resp.ok) {
      throw new Error('API error: ' + resp.status);
    }
    return resp.json();
  }

  /**
   * Show loading state in a container.
   * @param {HTMLElement} el
   */
  function showLoading(el) {
    el.innerHTML = '<div class="widget-loading">Loading...</div>';
  }

  /**
   * Show error state in a container.
   * @param {HTMLElement} el
   * @param {string} msg
   */
  function showError(el, msg) {
    el.innerHTML = '<div class="widget-error">' + escapeHtml(msg) + '</div>';
  }

  /**
   * Escape HTML to prevent XSS.
   * @param {string} str
   * @returns {string}
   */
  function escapeHtml(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  /**
   * Truncate text to a maximum length.
   * @param {string} text
   * @param {number} maxLen
   * @returns {string}
   */
  function truncate(text, maxLen) {
    if (!text || text.length <= maxLen) return text || '';
    return text.substring(0, maxLen) + '\u2026';
  }

  /**
   * Get today's date as MM-DD string.
   * @returns {string}
   */
  function todayMMDD() {
    var now = new Date();
    var mm = String(now.getMonth() + 1).padStart(2, '0');
    var dd = String(now.getDate()).padStart(2, '0');
    return mm + '-' + dd;
  }

  /**
   * Get today's date formatted for display.
   * @returns {string}
   */
  function todayFormatted() {
    var now = new Date();
    var months = ['January','February','March','April','May','June',
                  'July','August','September','October','November','December'];
    return months[now.getMonth()] + ' ' + now.getDate();
  }

  // Expose utilities globally for widget pages
  window.AtlasWidget = {
    API_BASE: API_BASE,
    params: params,
    formatYear: formatYear,
    formatYearRange: formatYearRange,
    confidenceLevel: confidenceLevel,
    apiFetch: apiFetch,
    showLoading: showLoading,
    showError: showError,
    escapeHtml: escapeHtml,
    truncate: truncate,
    todayMMDD: todayMMDD,
    todayFormatted: todayFormatted,
  };
})();
