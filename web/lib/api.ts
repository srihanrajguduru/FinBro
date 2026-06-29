/**
 * --------------------------------------------------------
 * File: web/lib/api.ts
 * Purpose: Frontend API Client for Backend Integration
 * Responsibilities: Performs typed HTTP requests to the FastAPI backend endpoints
 *                   handling authorization, request/response lifecycle, and JSON serialization.
 * Author: Srihan Raj Guduru
 * --------------------------------------------------------
 */

import { env } from "./env";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  user_type: "student" | "professional";
  monthly_salary: number;
  monthly_spending_limit: number | null;
  onboarding_complete: boolean;
  fbt_balance: number;
  created_at: string;
}

export interface Transaction {
  id: string;
  user_id: string;
  amount: number;
  transaction_type: "income" | "expense";
  category: string;
  description: string;
  date: string;
  created_at: string;
}

export interface TransactionSummary {
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  savings_target: number;
  by_category: Record<string, number>;
}

export interface Goal {
  id: string;
  user_id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  monthly_target: number;
  deadline: string | null;
  status: "active" | "completed" | "paused";
  created_at: string;
  updated_at: string;
}

export interface Debt {
  id: string;
  user_id: string;
  name: string;
  balance: number;
  interest_rate: number;
  minimum_payment: number;
  created_at: string;
  updated_at: string;
}

export interface PayoffSimulation {
  strategy: string;
  total_months: number;
  total_interest: number;
  total_paid: number;
  schedule: Array<{
    month: number;
    debt_name: string;
    payment: number;
    interest: number;
    principal: number;
    remaining_balance: number;
  }>;
  debts_eliminated: string[];
}

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  read: boolean;
  created_at: string;
}

export interface RewardBalance {
  fbt_balance: number;
  total_earned: number;
  transactions: Array<{
    id: string;
    amount: number;
    reward_type: string;
    description: string;
    tx_hash: string | null;
    created_at: string;
  }>;
}

export interface RetirementProjection {
  id: string;
  projected_balance: number;
  years_to_retirement: number;
  current_age: number;
  retirement_age: number;
  current_savings: number;
  monthly_contribution: number;
  annual_return_rate: number;
  created_at: string;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = env.NEXT_PUBLIC_API_URL;
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };
    if (token) headers.Authorization = `Bearer ${token}`;

    const res = await fetch(`${this.baseUrl}${path}`, { ...options, headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Request failed");
    }
    if (res.status === 204) return undefined as T;
    return res.json();
  }

  // Auth
  /**
   * Registers a new user account on the platform.
   *
   * @param email The user's email address
   * @param password The user's plain text password
   * @param full_name The user's full name
   * @returns A token response containing JWT access and refresh tokens
   */
  register(email: string, password: string, full_name: string) {
    return this.request<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    });
  }

  /**
   * Authenticates an existing user's credentials.
   *
   * @param email The user's email address
   * @param password The user's password
   * @returns A token response containing JWT access and refresh tokens
   */
  login(email: string, password: string) {
    return this.request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  /**
   * Authenticates using the preconfigured Demo User account (seeds demo data on first call).
   *
   * @returns A token response with static demo JWT tokens
   */
  demoLogin() {
    return this.request<TokenResponse>("/auth/demo", { method: "POST" });
  }

  me() {
    return this.request<User>("/auth/me");
  }

  onboarding(data: { user_type: string; monthly_salary: number; monthly_spending_limit?: number }) {
    return this.request<User>("/auth/onboarding", { method: "POST", body: JSON.stringify(data) });
  }

  // Transactions
  getTransactions() {
    return this.request<Transaction[]>("/transactions");
  }

  getSummary() {
    return this.request<TransactionSummary>("/transactions/summary");
  }

  createTransaction(data: Partial<Transaction>) {
    return this.request<Transaction>("/transactions", { method: "POST", body: JSON.stringify(data) });
  }

  deleteTransaction(id: string) {
    return this.request<void>(`/transactions/${id}`, { method: "DELETE" });
  }

  // Goals
  getGoals() {
    return this.request<Goal[]>("/goals");
  }

  createGoal(data: { name: string; target_amount: number; current_amount?: number; deadline?: string }) {
    return this.request<Goal>("/goals", { method: "POST", body: JSON.stringify(data) });
  }

  updateGoal(id: string, data: Partial<Goal>) {
    return this.request<Goal>(`/goals/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  deleteGoal(id: string) {
    return this.request<void>(`/goals/${id}`, { method: "DELETE" });
  }

  // Debts
  getDebts() {
    return this.request<Debt[]>("/debts");
  }

  createDebt(data: { name: string; balance: number; interest_rate: number; minimum_payment: number }) {
    return this.request<Debt>("/debts", { method: "POST", body: JSON.stringify(data) });
  }

  /**
   * Simulates the payoff duration and interest generated using different repayment strategies.
   *
   * @param strategy The repayment strategy ("avalanche" or "snowball")
   * @param extra_payment The extra monthly payment amount above the minimums
   * @returns A detailed simulation schedule and metrics
   */
  simulatePayoff(strategy: string, extra_payment: number) {
    return this.request<PayoffSimulation>("/debts/payoff/simulate", {
      method: "POST",
      body: JSON.stringify({ strategy, extra_payment }),
    });
  }

  // Expenses
  getLimitStatus() {
    return this.request<{ limit: number; spent: number; remaining: number; percentage: number; warning_level: string }>(
      "/expenses/limit-status"
    );
  }

  createExpense(data: { amount: number; category: string; description?: string }) {
    return this.request<Transaction>("/expenses", { method: "POST", body: JSON.stringify(data) });
  }

  // Predictions
  createRetirement(data: {
    current_age: number;
    retirement_age: number;
    current_savings: number;
    monthly_contribution: number;
    annual_return_rate?: number;
  }) {
    return this.request<RetirementProjection>("/predict/retirement", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  getRetirements() {
    return this.request<RetirementProjection[]>("/predict/retirement");
  }

  // Rewards
  getRewardBalance() {
    return this.request<RewardBalance>("/rewards/balance");
  }

  // Notifications
  getNotifications() {
    return this.request<Notification[]>("/notifications");
  }

  markNotificationRead(id: string) {
    return this.request<Notification>(`/notifications/${id}/read`, { method: "PUT" });
  }

  markAllNotificationsRead() {
    return this.request<{ marked_read: number }>("/notifications/read-all", { method: "PUT" });
  }

  // Chat
  /**
   * Sends a user chat message to the backend AI agent.
   *
   * @param message The user's chat message query
   * @returns The AI reply and detected intent category
   */
  chat(message: string) {
    return this.request<{ reply: string; intent: string }>("/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
  }
}

export const api = new ApiClient();
