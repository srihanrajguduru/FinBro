"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function DebtPage() {
  const queryClient = useQueryClient();
  const { data: debts } = useQuery({ queryKey: ["debts"], queryFn: () => api.getDebts() });
  const [strategy, setStrategy] = useState<"avalanche" | "snowball">("avalanche");
  const [extraPayment, setExtraPayment] = useState("0");
  const [simulation, setSimulation] = useState<Awaited<ReturnType<typeof api.simulatePayoff>> | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", balance: "", rate: "", minPayment: "" });

  const createMutation = useMutation({
    mutationFn: () =>
      api.createDebt({
        name: form.name,
        balance: parseFloat(form.balance),
        interest_rate: parseFloat(form.rate),
        minimum_payment: parseFloat(form.minPayment),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["debts"] });
      toast.success("Debt added");
      setShowForm(false);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  async function runSimulation() {
    try {
      const result = await api.simulatePayoff(strategy, parseFloat(extraPayment) || 0);
      setSimulation(result);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Simulation failed");
    }
  }

  const totalDebt = (debts || []).reduce((s, d) => s + d.balance, 0);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Debt Payoff</h1>
          <p className="text-muted-foreground">Total debt: {formatCurrency(totalDebt)}</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>{showForm ? "Cancel" : "Add Debt"}</Button>
      </div>

      {showForm && (
        <Card>
          <CardContent className="grid gap-4 pt-6 md:grid-cols-4">
            <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
            <div><Label>Balance</Label><Input type="number" value={form.balance} onChange={(e) => setForm({ ...form, balance: e.target.value })} /></div>
            <div><Label>Rate (%)</Label><Input type="number" value={form.rate} onChange={(e) => setForm({ ...form, rate: e.target.value })} /></div>
            <div><Label>Min Payment</Label><Input type="number" value={form.minPayment} onChange={(e) => setForm({ ...form, minPayment: e.target.value })} /></div>
            <Button className="md:col-span-4" onClick={() => createMutation.mutate()}>Add Debt</Button>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {(debts || []).map((debt) => (
          <Card key={debt.id}>
            <CardHeader><CardTitle>{debt.name}</CardTitle></CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-secondary">{formatCurrency(debt.balance)}</p>
              <p className="text-sm text-muted-foreground">{debt.interest_rate}% APR · Min {formatCurrency(debt.minimum_payment)}/mo</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {(debts?.length ?? 0) > 0 && (
        <Card>
          <CardHeader><CardTitle>Payoff Simulation</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-4">
              <div className="flex gap-2">
                {(["avalanche", "snowball"] as const).map((s) => (
                  <Button key={s} variant={strategy === s ? "default" : "outline"} size="sm" onClick={() => setStrategy(s)} className="capitalize">
                    {s}
                  </Button>
                ))}
              </div>
              <div className="flex items-center gap-2">
                <Label>Extra/mo</Label>
                <Input type="number" className="w-24" value={extraPayment} onChange={(e) => setExtraPayment(e.target.value)} />
              </div>
              <Button onClick={runSimulation}>Simulate</Button>
            </div>
            {simulation && (
              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-lg bg-muted p-4"><p className="text-sm text-muted-foreground">Months</p><p className="text-xl font-bold">{simulation.total_months}</p></div>
                <div className="rounded-lg bg-muted p-4"><p className="text-sm text-muted-foreground">Total Interest</p><p className="text-xl font-bold text-secondary">{formatCurrency(simulation.total_interest)}</p></div>
                <div className="rounded-lg bg-muted p-4"><p className="text-sm text-muted-foreground">Total Paid</p><p className="text-xl font-bold">{formatCurrency(simulation.total_paid)}</p></div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
