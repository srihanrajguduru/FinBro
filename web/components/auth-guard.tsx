/**
 * --------------------------------------------------------
 * File: web/components/auth-guard.tsx
 * Purpose: Authentication Route Guard Component
 * Responsibilities: Protects page routes by checking the JWT session token,
 *                   fetching current user profile, and enforcing onboarding completion.
 * Author: Srihan Raj Guduru
 * --------------------------------------------------------
 */

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import { api } from "@/lib/api";

/**
 * Route guard component that wraps pages requiring authentication.
 * Redirects to /login if no token exists, or /onboarding if onboarding is incomplete.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { accessToken, user, setUser } = useAuthStore();

  useEffect(() => {
    if (!accessToken) {
      router.replace("/login");
      return;
    }
    if (!user) {
      api.me().then(setUser).catch(() => router.replace("/login"));
      return;
    }
    if (!user.onboarding_complete) {
      router.replace("/onboarding");
    }
  }, [accessToken, user, router, setUser]);

  if (!accessToken) return null;
  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!user.onboarding_complete) return null;

  return <>{children}</>;
}
