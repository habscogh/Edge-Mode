/**
 * Date utilities for Edge Mode
 * Handles local timezone date formatting consistently
 */

/**
 * Get the current date in user's local timezone as YYYY-MM-DD string
 * This is important because toISOString() converts to UTC which can shift the date
 */
export function getLocalDateString() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Get a Date object's date in local timezone as YYYY-MM-DD string
 */
export function formatLocalDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}
