"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Grid3X3, Home, Sparkles, Trophy, Users } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "Home", icon: Home },
  { href: "/groups", label: "Groups", icon: Grid3X3 },
  { href: "/teams", label: "Teams", icon: Users },
  { href: "/rankings", label: "Rankings", icon: BarChart3 },
  { href: "/predictions", label: "Predictions", icon: Sparkles },
  { href: "/simulation", label: "Simulation", icon: Trophy },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex shrink-0 items-center gap-2.5">
          <div className="flex size-9 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-700 text-lg shadow-lg shadow-emerald-500/20">
            ⚽
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-bold leading-none tracking-tight">
              FIFA2026LM
            </p>
            <p className="text-[10px] uppercase tracking-widest text-muted-foreground">
              Prediction Engine
            </p>
          </div>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active =
              href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link key={href} href={href}>
                <Button
                  variant={active ? "secondary" : "ghost"}
                  size="sm"
                  className={cn(
                    "gap-1.5",
                    active && "bg-emerald-500/10 text-emerald-400"
                  )}
                >
                  <Icon className="size-3.5" />
                  {label}
                </Button>
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-1">
          <ThemeToggle />
        </div>
      </div>

      <nav className="flex gap-1 overflow-x-auto border-t border-border/40 px-4 py-2 md:hidden">
        {NAV_ITEMS.map(({ href, label }) => {
          const active =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link key={href} href={href}>
              <Button
                variant={active ? "secondary" : "ghost"}
                size="xs"
                className={cn(
                  "shrink-0",
                  active && "bg-emerald-500/10 text-emerald-400"
                )}
              >
                {label}
              </Button>
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
