/**
 * --------------------------------------------------------
 * File: web/components/providers.tsx
 * Purpose: Client Application Providers Wrapper
 * Responsibilities: Wraps the app with ThemeProvider, TanStack QueryClientProvider,
 *                   and sets up the global toast notification layout (Toaster).
 * Author: Srihan Raj Guduru
 * --------------------------------------------------------
 */

"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { Toaster } from "sonner";
import { useState } from "react";

/**
 * Root providers wrapper for Client Components.
 * Configures the QueryClient cache settings and UI styling parameters.
 */
export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
        {children}
        <Toaster richColors position="top-right" />
      </ThemeProvider>
    </QueryClientProvider>
  );
}
