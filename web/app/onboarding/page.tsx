"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

export default function OnboardingPage() {
  const router = useRouter();
  const { accessToken, setUser } = useAuthStore();
  const [userType, setUserType] = useState<"student" | "professional">("professional");
  const [salary, setSalary] = useState("");
  const [spendingLimit, setSpendingLimit] = useState("");
  const [loading, setLoading] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!accessToken) {
      router.replace("/login");
    } else {
      Promise.resolve().then(() => setReady(true));
    }
  }, [accessToken, router]);

  if (!ready) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await api.onboarding({
        user_type: userType,
        monthly_salary: parseFloat(salary),
        monthly_spending_limit: userType === "student" ? parseFloat(spendingLimit) : undefined,
      });
      setUser(user);
      toast.success("Welcome to FinBro!");
      router.push("/dashboard");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Onboarding failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle className="text-2xl text-primary">Let&apos;s set up your profile</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-3">
              <Label>I am a...</Label>
              <div className="grid grid-cols-2 gap-3">
                {(["professional", "student"] as const).map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setUserType(type)}
                    className={`rounded-lg border p-4 text-left capitalize transition-colors ${
                      userType === type ? "border-primary bg-primary/10" : "border-border hover:bg-muted"
                    }`}
                  >
                    {type}
                    <p className="mt-1 text-xs text-muted-foreground">
                      {type === "professional" ? "20% savings target" : "15% savings target + spending limit"}
                    </p>
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="salary">Monthly Income ($)</Label>
              <Input id="salary" type="number" min="0" step="0.01" value={salary} onChange={(e) => setSalary(e.target.value)} required />
            </div>
            {userType === "student" && (
              <div className="space-y-2">
                <Label htmlFor="limit">Monthly Spending Limit ($)</Label>
                <Input id="limit" type="number" min="0" step="0.01" value={spendingLimit} onChange={(e) => setSpendingLimit(e.target.value)} required />
              </div>
            )}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Saving..." : "Continue to Dashboard"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
