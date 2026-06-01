"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { formatProbability } from "@/lib/constants/teams";

interface ProbabilityBarProps {
  label: string;
  value: number;
  color?: string;
  delay?: number;
  className?: string;
}

export function ProbabilityBar({
  label,
  value,
  color = "bg-emerald-500",
  delay = 0,
  className,
}: ProbabilityBarProps) {
  const pct = Math.min(Math.max(value * 100, 0), 100);

  return (
    <div className={cn("space-y-1.5", className)}>
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-foreground">{label}</span>
        <span className="tabular-nums text-muted-foreground">
          {formatProbability(value)}
        </span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-muted/60">
        <motion.div
          className={cn("h-full rounded-full", color)}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: "easeOut", delay }}
        />
      </div>
    </div>
  );
}

interface MultiProbabilityBarsProps {
  homeTeam: string;
  awayTeam: string;
  homeWin: number;
  draw: number;
  awayWin: number;
}

export function MultiProbabilityBars({
  homeTeam,
  awayTeam,
  homeWin,
  draw,
  awayWin,
}: MultiProbabilityBarsProps) {
  return (
    <div className="space-y-4">
      <ProbabilityBar
        label={`${homeTeam} Win`}
        value={homeWin}
        color="bg-emerald-500"
        delay={0}
      />
      <ProbabilityBar
        label="Draw"
        value={draw}
        color="bg-amber-500"
        delay={0.1}
      />
      <ProbabilityBar
        label={`${awayTeam} Win`}
        value={awayWin}
        color="bg-sky-500"
        delay={0.2}
      />
    </div>
  );
}
