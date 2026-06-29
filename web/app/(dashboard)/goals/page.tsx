"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function GoalsPage() {
  const queryClient = useQueryClient();
  const { data: goals, isLoading } = useQuery({ queryKey: ["goals"], queryFn: () => api.getGoals() });
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [target, setTarget] = useState("");
  const [current, setCurrent] = useState("0");

  const createMutation = useMutation({
    mutationFn: () => api.createGoal({ name, target_amount: parseFloat(target), current_amount: parseFloat(current) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      toast.success("Goal created!");
      setShowForm(false);
      setName("");
      setTarget("");
      setCurrent("0");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, amount }: { id: string; amount: number }) =>
      api.updateGoal(id, { current_amount: amount }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      queryClient.invalidateQueries({ queryKey: ["rewards"] });
      toast.success("Progress updated!");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteGoal(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      toast.success("Goal deleted");
    },
  });

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Goals</h1>
          <p className="text-muted-foreground">Track savings goals and earn 100 FBT on completion</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>{showForm ? "Cancel" : "New Goal"}</Button>
      </div>

      {showForm && (
        <Card>
          <CardContent className="pt-6">
            <div className="grid gap-4 md:grid-cols-3">
              <div><Label>Name</Label><Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Emergency Fund" /></div>
              <div><Label>Target ($)</Label><Input type="number" value={target} onChange={(e) => setTarget(e.target.value)} /></div>
              <div><Label>Current ($)</Label><Input type="number" value={current} onChange={(e) => setCurrent(e.target.value)} /></div>
            </div>
            <Button className="mt-4" onClick={() => createMutation.mutate()} disabled={!name || !target}>Create Goal</Button>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {(goals || []).map((goal, i) => {
          const pct = Math.min((goal.current_amount / goal.target_amount) * 100, 100);
          return (
            <motion.div key={goal.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }}>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>{goal.name}</CardTitle>
                  <span className={`rounded-full px-2 py-1 text-xs capitalize ${goal.status === "completed" ? "bg-primary/20 text-primary" : "bg-muted"}`}>
                    {goal.status}
                  </span>
                </CardHeader>
                <CardContent>
                  <div className="mb-2 flex justify-between text-sm">
                    <span>{formatCurrency(goal.current_amount)} / {formatCurrency(goal.target_amount)}</span>
                    <span>{pct.toFixed(0)}%</span>
                  </div>
                  <div className="h-3 overflow-hidden rounded-full bg-muted">
                    <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pct}%` }} />
                  </div>
                  <p className="mt-2 text-xs text-muted-foreground">Monthly target: {formatCurrency(goal.monthly_target)}</p>
                  {goal.status === "active" && (
                    <div className="mt-4 flex gap-2">
                      <Button size="sm" onClick={() => updateMutation.mutate({ id: goal.id, amount: goal.current_amount + 100 })}>
                        +$100
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => deleteMutation.mutate(goal.id)}>Delete</Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
      {!isLoading && !goals?.length && <p className="text-center text-muted-foreground">No goals yet. Create your first one!</p>}
    </div>
  );
}
