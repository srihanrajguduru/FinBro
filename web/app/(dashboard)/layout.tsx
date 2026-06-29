"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Target,
  CreditCard,
  Gift,
  Bell,
  MessageCircle,
  HelpCircle,
  LogOut,
  Moon,
  Sun,
} from "lucide-react";
import { useTheme } from "next-themes";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/store";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/debt", label: "Debt", icon: CreditCard },
  { href: "/goals", label: "Goals", icon: Target },
  { href: "/quiz", label: "Quiz", icon: HelpCircle },
  { href: "/chat", label: "AI Chat", icon: MessageCircle },
  { href: "/rewards", label: "Rewards", icon: Gift },
  { href: "/notifications", label: "Notifications", icon: Bell },
];

function DashboardNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { theme, setTheme } = useTheme();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <aside className="flex w-64 flex-col border-r border-border bg-card/50 backdrop-blur-md">
      <div className="border-b border-border p-6">
        <h1 className="text-xl font-bold text-primary">FinBro</h1>
        <p className="mt-1 truncate text-xs text-muted-foreground">{user?.email}</p>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
              pathname === href
                ? "bg-primary text-white"
                : "text-foreground hover:bg-muted"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
      <div className="space-y-2 border-t border-border p-4">
        <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
          {theme === "dark" ? <Sun className="mr-2 h-4 w-4" /> : <Moon className="mr-2 h-4 w-4" />}
          Toggle theme
        </Button>
        <Button variant="ghost" size="sm" className="w-full justify-start text-secondary" onClick={handleLogout}>
          <LogOut className="mr-2 h-4 w-4" />
          Sign out
        </Button>
      </div>
    </aside>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <DashboardNav />
        <motion.main
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="flex-1 overflow-auto p-8"
        >
          {children}
        </motion.main>
      </div>
    </AuthGuard>
  );
}
