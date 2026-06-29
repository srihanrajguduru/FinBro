"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { useAuthStore } from "@/lib/store";

const CHART_COLORS = ["#0d5c4a", "#ff6b6b", "#4ecdc4", "#ffe66d", "#95e1d3", "#f38181", "#aa96da"];

export default function DashboardPage() {
  const { user } = useAuthStore();
  const { data: summary, isLoading } = useQuery({ queryKey: ["summary"], queryFn: () => api.getSummary() });
  const { data: transactions } = useQuery({ queryKey: ["transactions"], queryFn: () => api.getTransactions() });

  const categoryData = summary
    ? Object.entries(summary.by_category).map(([name, value]) => ({ name, value }))
    : [];

  const savingsTargetMet = summary ? summary.net_savings >= summary.savings_target : false;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back, {user?.full_name || "FinBro user"}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Income", value: summary?.total_income, color: "text-primary" },
          { label: "Expenses", value: summary?.total_expenses, color: "text-secondary" },
          { label: "Net Savings", value: summary?.net_savings, color: savingsTargetMet ? "text-primary" : "text-foreground" },
          { label: "Savings Rate", value: summary?.savings_rate, isPercent: true },
        ].map((stat, i) => (
          <motion.div key={stat.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <p className={`text-2xl font-bold ${stat.color || ""}`}>
                  {isLoading ? "..." : stat.isPercent ? formatPercent(stat.value || 0) : formatCurrency(stat.value || 0)}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {summary && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <span className="text-sm">Savings target: {formatCurrency(summary.savings_target)}</span>
              <span className={`text-sm font-medium ${savingsTargetMet ? "text-primary" : "text-secondary"}`}>
                {savingsTargetMet ? "Target met!" : `${formatPercent(summary.savings_rate)} of income saved`}
              </span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary transition-all"
                style={{ width: `${Math.min((summary.net_savings / summary.savings_target) * 100, 100)}%` }}
              />
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Spending by Category</CardTitle></CardHeader>
          <CardContent>
            {categoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {categoryData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="py-12 text-center text-muted-foreground">No expense data this month</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Recent Transactions</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(transactions || []).slice(0, 5).map((tx) => (
                <div key={tx.id} className="flex items-center justify-between rounded-lg bg-muted/50 px-3 py-2">
                  <div>
                    <p className="text-sm font-medium">{tx.description || tx.category}</p>
                    <p className="text-xs text-muted-foreground capitalize">{tx.category}</p>
                  </div>
                  <span className={tx.transaction_type === "income" ? "text-primary" : "text-secondary"}>
                    {tx.transaction_type === "income" ? "+" : "-"}{formatCurrency(tx.amount)}
                  </span>
                </div>
              ))}
              {!transactions?.length && <p className="py-8 text-center text-muted-foreground">No transactions yet</p>}
            </div>
          </CardContent>
        </Card>
      </div>

      {categoryData.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Category Breakdown</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                <Bar dataKey="value" fill="#0d5c4a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
