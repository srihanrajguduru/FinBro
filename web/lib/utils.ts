/**
 * --------------------------------------------------------
 * File: web/lib/utils.ts
 * Purpose: Client Utility Functions
 * Responsibilities: Contains formatting helper functions (currency, percentage)
 *                   and CSS class merger utility (cn).
 * Author: Srihan Raj Guduru
 * --------------------------------------------------------
 */

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combines CSS class names and resolves tailwind CSS conflicts.
 *
 * @param inputs CSS classes or dynamic conditions
 * @returns Combined and sanitized class list string
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Formats a numeric amount to USD currency string.
 *
 * @param amount The numeric amount to format
 * @returns Formatted currency string (e.g. $1,250.00)
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(amount);
}

/**
 * Formats a numeric value to a percentage string.
 *
 * @param value The percentage value (e.g. 15.5)
 * @returns Formatted percentage string (e.g. 15.5%)
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}
