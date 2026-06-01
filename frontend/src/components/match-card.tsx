import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getTeamFlag } from "@/lib/constants/teams";
import type { PredictResponse } from "@/lib/types/api";
import { MultiProbabilityBars } from "./probability-bar";

interface MatchCardProps {
  prediction: PredictResponse;
  homeElo?: number | null;
  awayElo?: number | null;
}

export function MatchCard({ prediction, homeElo, awayElo }: MatchCardProps) {
  const {
    home_team,
    away_team,
    home_win,
    draw,
    away_win,
    confidence,
  } = prediction;

  return (
    <Card className="overflow-hidden border-border/60 bg-card/80 backdrop-blur-sm">
      <CardHeader className="border-b border-border/40 bg-muted/20 pb-4">
        <div className="flex items-center justify-between gap-4">
          <div className="flex flex-1 items-center justify-end gap-3 text-right">
            <div>
              <CardTitle className="text-lg">{home_team}</CardTitle>
              {homeElo != null && (
                <CardDescription>ELO {homeElo.toFixed(0)}</CardDescription>
              )}
            </div>
            <span className="text-3xl" aria-hidden>
              {getTeamFlag(home_team)}
            </span>
          </div>

          <div className="flex flex-col items-center px-2">
            <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              vs
            </span>
            <Badge variant="secondary" className="mt-1 tabular-nums">
              {(confidence * 100).toFixed(0)}% conf.
            </Badge>
          </div>

          <div className="flex flex-1 items-center gap-3">
            <span className="text-3xl" aria-hidden>
              {getTeamFlag(away_team)}
            </span>
            <div>
              <CardTitle className="text-lg">{away_team}</CardTitle>
              {awayElo != null && (
                <CardDescription>ELO {awayElo.toFixed(0)}</CardDescription>
              )}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-6">
        <MultiProbabilityBars
          homeTeam={home_team}
          awayTeam={away_team}
          homeWin={home_win}
          draw={draw}
          awayWin={away_win}
        />
      </CardContent>
    </Card>
  );
}
