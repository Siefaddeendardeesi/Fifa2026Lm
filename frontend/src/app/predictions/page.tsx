"use client";

import { useMemo, useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { ErrorState } from "@/components/error-state";
import { MatchCard } from "@/components/match-card";
import { PageHeader } from "@/components/page-header";
import { CardGridSkeleton } from "@/components/loading-skeletons";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getTeamFlag } from "@/lib/constants/teams";
import { usePredict } from "@/lib/hooks/usePredict";
import { useRankings } from "@/lib/hooks/useRankings";
import { useTeams } from "@/lib/hooks/useTeams";

export default function PredictionsPage() {
  const { data: teamsData, isLoading: teamsLoading, error: teamsError } =
    useTeams();
  const { data: eloRankings } = useRankings("elo", 48);
  const predict = usePredict();

  const teamNames = useMemo(
    () => teamsData?.teams.map((t) => t.name).sort() ?? [],
    [teamsData]
  );

  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");

  const eloMap = useMemo(() => {
    const map = new Map<string, number>();
    eloRankings?.rankings.forEach((r) => {
      if (r.elo != null) map.set(r.team, r.elo);
    });
    return map;
  }, [eloRankings]);

  function handlePredict() {
    if (!homeTeam || !awayTeam || homeTeam === awayTeam) return;
    predict.mutate({
      home_team: homeTeam,
      away_team: awayTeam,
      neutral: true,
    });
  }

  const canPredict =
    homeTeam && awayTeam && homeTeam !== awayTeam && !predict.isPending;

  return (
    <div className="mx-auto max-w-4xl space-y-8 px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader
        badge="Match Predictor"
        title="Head-to-Head Predictions"
        description="Select two teams to get ML-powered win, draw, and loss probabilities with confidence scores."
      />

      <Card className="border-border/60 bg-card/70">
        <CardHeader>
          <CardTitle>Match Selector</CardTitle>
          <CardDescription>
            Neutral venue assumption — no home advantage applied
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {teamsLoading && <CardGridSkeleton count={2} />}
          {teamsError && (
            <ErrorState message={(teamsError as Error).message} />
          )}

          {teamNames.length > 0 && (
            <>
              <div className="grid gap-4 sm:grid-cols-[1fr,auto,1fr] sm:items-end">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Home Team</label>
                  <Select
                    value={homeTeam}
                    onValueChange={(v) => setHomeTeam(v ?? "")}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select home team" />
                    </SelectTrigger>
                    <SelectContent>
                      {teamNames.map((name) => (
                        <SelectItem key={`home-${name}`} value={name}>
                          {getTeamFlag(name)} {name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="hidden py-2 text-center text-sm font-bold text-muted-foreground sm:block">
                  VS
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Away Team</label>
                  <Select
                    value={awayTeam}
                    onValueChange={(v) => setAwayTeam(v ?? "")}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select away team" />
                    </SelectTrigger>
                    <SelectContent>
                      {teamNames.map((name) => (
                        <SelectItem key={`away-${name}`} value={name}>
                          {getTeamFlag(name)} {name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {homeTeam === awayTeam && homeTeam && (
                <p className="text-sm text-destructive">
                  Please select two different teams.
                </p>
              )}

              <Button
                onClick={handlePredict}
                disabled={!canPredict}
                className="w-full gap-2 sm:w-auto"
                size="lg"
              >
                {predict.isPending ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  <Sparkles className="size-4" />
                )}
                Predict Match Outcome
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      {predict.error && (
        <ErrorState message={(predict.error as Error).message} />
      )}

      {predict.data && (
        <MatchCard
          prediction={predict.data}
          homeElo={eloMap.get(predict.data.home_team)}
          awayElo={eloMap.get(predict.data.away_team)}
        />
      )}
    </div>
  );
}
