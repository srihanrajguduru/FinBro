"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function RewardsPage() {
  const { data, isLoading } = useQuery({ queryKey: ["rewards"], queryFn: () => api.getRewardBalance() });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Rewards</h1>
        <p className="text-muted-foreground">Earn FBT tokens for financial milestones</p>
      </div>

      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
        <Card className="bg-gradient-to-br from-primary/20 to-secondary/10">
          <CardContent className="pt-8 text-center">
            <p className="text-sm text-muted-foreground">Your Balance</p>
            <p className="text-5xl font-bold text-primary">{isLoading ? "..." : `${data?.fbt_balance ?? 0} FBT`}</p>
            <p className="mt-2 text-sm text-muted-foreground">Total earned: {formatCurrency(data?.total_earned ?? 0).replace("$", "")} FBT</p>
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid gap-4 md:grid-cols-3">
        {[
          { label: "Complete a Goal", amount: 100 },
          { label: "Hit Monthly Savings", amount: 50 },
          { label: "Debt Milestone", amount: 75 },
        ].map((r) => (
          <Card key={r.label}>
            <CardContent className="pt-6 text-center">
              <p className="text-2xl font-bold text-primary">{r.amount} FBT</p>
              <p className="text-sm text-muted-foreground">{r.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>Transaction History</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {(data?.transactions || []).map((tx) => (
              <div key={tx.id} className="flex items-center justify-between rounded-lg bg-muted/50 px-4 py-3">
                <div>
                  <p className="font-medium">{tx.description}</p>
                  <p className="text-xs text-muted-foreground capitalize">{tx.reward_type.replace("_", " ")}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-primary">+{tx.amount} FBT</p>
                  {tx.tx_hash && <p className="text-xs text-muted-foreground truncate max-w-[120px]">{tx.tx_hash}</p>}
                </div>
              </div>
            ))}
            {!data?.transactions?.length && <p className="py-8 text-center text-muted-foreground">No rewards yet</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
