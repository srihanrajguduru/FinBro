import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 bg-background p-8">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-primary">FinBro</h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Gamified personal finance — save smarter, crush debt, earn rewards
        </p>
      </div>
      <div className="flex gap-4">
        <Button asChild size="lg">
          <Link href="/login">Sign In</Link>
        </Button>
        <Button asChild variant="outline" size="lg">
          <Link href="/register">Get Started</Link>
        </Button>
      </div>
    </div>
  );
}
