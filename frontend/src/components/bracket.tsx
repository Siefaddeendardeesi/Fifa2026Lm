"use client";

import { motion } from "framer-motion";
import { getTeamFlag } from "@/lib/constants/teams";
import { cn } from "@/lib/utils";

interface BracketTeam {
  team: string;
  probability?: number;
}

interface BracketProps {
  champion: BracketTeam[];
  finalists: BracketTeam[];
  className?: string;
}

function BracketSlot({
  team,
  probability,
  highlight = false,
}: BracketTeam & { highlight?: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "flex items-center justify-between gap-2 rounded-lg border px-3 py-2 text-sm",
        highlight
          ? "border-emerald-500/40 bg-emerald-500/10"
          : "border-border/60 bg-card/60"
      )}
    >
      <div className="flex items-center gap-2 min-w-0">
        <span aria-hidden>{getTeamFlag(team)}</span>
        <span className="truncate font-medium">{team}</span>
      </div>
      {probability != null && (
        <span className="shrink-0 tabular-nums text-xs text-muted-foreground">
          {(probability * 100).toFixed(1)}%
        </span>
      )}
    </motion.div>
  );
}

export function Bracket({ champion, finalists, className }: BracketProps) {
  const topFinalists = finalists.slice(0, 8);
  const topChampion = champion.slice(0, 4);

  return (
    <div className={cn("grid gap-6 lg:grid-cols-3", className)}>
      <div className="space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Semi-Final Contenders
        </h3>
        <div className="space-y-2">
          {topFinalists.slice(0, 4).map((entry) => (
            <BracketSlot key={entry.team} {...entry} />
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Finalists
        </h3>
        <div className="space-y-2">
          {topFinalists.slice(0, 4).map((entry) => (
            <BracketSlot key={`final-${entry.team}`} {...entry} />
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-emerald-400">
          Champion
        </h3>
        <div className="space-y-2">
          {topChampion.map((entry, i) => (
            <BracketSlot key={`champ-${entry.team}`} {...entry} highlight={i === 0} />
          ))}
        </div>
      </div>
    </div>
  );
}
