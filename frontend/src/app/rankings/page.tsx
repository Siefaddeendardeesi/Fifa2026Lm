"use client";

import { useMemo, useState } from "react";
import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import { ErrorState } from "@/components/error-state";
import { PageHeader } from "@/components/page-header";
import { TableSkeleton } from "@/components/loading-skeletons";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatScore, getTeamFlag } from "@/lib/constants/teams";
import { useMergedRankings } from "@/lib/hooks/useRankings";
import { cn } from "@/lib/utils";

type SortKey = "rank" | "team" | "elo" | "model" | "hybrid";
type SortDir = "asc" | "desc";

export default function RankingsPage() {
  const { data, isLoading, error } = useMergedRankings(48);
  const [sortKey, setSortKey] = useState<SortKey>("rank");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const sorted = useMemo(() => {
    if (!data) return [];
    return [...data].sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case "team":
          cmp = a.team.localeCompare(b.team);
          break;
        case "elo":
          cmp = (a.elo ?? -1) - (b.elo ?? -1);
          break;
        case "model":
          cmp = (a.model ?? -1) - (b.model ?? -1);
          break;
        case "hybrid":
          cmp = (a.hybrid ?? -1) - (b.hybrid ?? -1);
          break;
        default:
          cmp = a.rank - b.rank;
      }
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "team" ? "asc" : "desc");
    }
  }

  function SortIcon({ column }: { column: SortKey }) {
    if (sortKey !== column) {
      return <ArrowUpDown className="ml-1 inline size-3 opacity-40" />;
    }
    return sortDir === "asc" ? (
      <ArrowUp className="ml-1 inline size-3 text-emerald-400" />
    ) : (
      <ArrowDown className="ml-1 inline size-3 text-emerald-400" />
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader
        badge="Power Rankings"
        title="Team Rankings"
        description="Compare ELO ratings, ML model scores, and hybrid rankings for all 48 World Cup nations."
      />

      <div className="flex flex-wrap gap-2">
        <Badge variant="secondary">ELO</Badge>
        <Badge variant="secondary">ML Model</Badge>
        <Badge className="bg-emerald-500/10 text-emerald-400">Hybrid</Badge>
      </div>

      {isLoading && <TableSkeleton rows={12} />}
      {error && <ErrorState message={(error as Error).message} />}

      {sorted.length > 0 && (
        <div className="overflow-hidden rounded-xl border border-border/60">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/30 hover:bg-muted/30">
                <TableHead className="w-16">
                  <Button
                    variant="ghost"
                    size="xs"
                    className="h-auto p-0 font-semibold"
                    onClick={() => toggleSort("rank")}
                  >
                    Rank
                    <SortIcon column="rank" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    size="xs"
                    className="h-auto p-0 font-semibold"
                    onClick={() => toggleSort("team")}
                  >
                    Team
                    <SortIcon column="team" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    size="xs"
                    className="h-auto p-0 font-semibold"
                    onClick={() => toggleSort("elo")}
                  >
                    ELO
                    <SortIcon column="elo" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    size="xs"
                    className="h-auto p-0 font-semibold"
                    onClick={() => toggleSort("model")}
                  >
                    Model
                    <SortIcon column="model" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    size="xs"
                    className="h-auto p-0 font-semibold"
                    onClick={() => toggleSort("hybrid")}
                  >
                    Hybrid
                    <SortIcon column="hybrid" />
                  </Button>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sorted.map((row, index) => (
                <TableRow
                  key={row.team}
                  className={cn(
                    "transition-colors hover:bg-muted/20",
                    index < 3 && "bg-emerald-500/5"
                  )}
                >
                  <TableCell className="font-bold tabular-nums text-muted-foreground">
                    {row.rank <= 48 ? row.rank : index + 1}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2.5">
                      <span className="text-xl" aria-hidden>
                        {getTeamFlag(row.team)}
                      </span>
                      <span className="font-medium">{row.team}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatScore(row.elo)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatScore(row.model)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums font-semibold text-emerald-400">
                    {formatScore(row.hybrid)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
