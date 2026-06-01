"use client";

import { motion } from "framer-motion";
import { BarChart3, Grid3X3, Sparkles, Trophy } from "lucide-react";
import { ErrorState } from "@/components/error-state";
import {
  CardGridSkeleton,
  PageHeaderSkeleton,
} from "@/components/loading-skeletons";
import { NavCard } from "@/components/nav-card";
import { ProbabilityBar } from "@/components/probability-bar";
import { TeamCard } from "@/components/team-card";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getTeamFlag, sortProbabilityEntries } from "@/lib/constants/teams";
import { useRankings } from "@/lib/hooks/useRankings";
import { useSimulationPreview } from "@/lib/hooks/useSimulate";

export default function HomePage() {
  const { data: rankings, isLoading: rankingsLoading, error: rankingsError } =
    useRankings("hybrid", 48);
  const {
    data: simulation,
    isLoading: simLoading,
    error: simError,
  } = useSimulationPreview();

  const topTeams = rankings?.rankings.slice(0, 4) ?? [];
  const championEntries = simulation
    ? sortProbabilityEntries(simulation.champion_probability, 5)
    : [];
  const topChampion = championEntries[0];

  return (
    <div className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-900/20 via-background to-background"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-32 top-20 size-96 rounded-full bg-emerald-500/5 blur-3xl"
      />

      <div className="relative mx-auto max-w-7xl space-y-12 px-4 py-10 sm:px-6 lg:px-8 lg:py-16">
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-6 text-center lg:text-left"
        >
          <Badge className="bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20">
            World Cup 2026 · USA · Mexico · Canada
          </Badge>
          <h1 className="mx-auto max-w-4xl text-4xl font-bold tracking-tight sm:text-5xl lg:mx-0 lg:text-6xl">
            FIFA World Cup 2026{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-emerald-600 bg-clip-text text-transparent">
              Predictions Engine
            </span>
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground lg:mx-0">
            Machine learning match predictions, ELO-powered rankings, and Monte
            Carlo tournament simulation for all 48 nations.
          </p>
        </motion.section>

        <section className="grid gap-4 lg:grid-cols-3">
          <Card className="border-border/60 bg-card/70 backdrop-blur-sm lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="size-5 text-emerald-400" />
                Top Predicted Teams
              </CardTitle>
              <CardDescription>
                Hybrid model rankings — ELO + ML combined
              </CardDescription>
            </CardHeader>
            <CardContent>
              {rankingsLoading && <CardGridSkeleton count={4} />}
              {rankingsError && (
                <ErrorState message={(rankingsError as Error).message} />
              )}
              {topTeams.length > 0 && (
                <div className="grid gap-3 sm:grid-cols-2">
                  {topTeams.map((team) => (
                    <TeamCard
                      key={team.team}
                      team={{
                        name: team.team,
                        group: null,
                        has_squad: false,
                      }}
                      rank={team.rank}
                      score={team.score}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 to-card/70 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Champion Probability</CardTitle>
              <CardDescription>
                {simulation
                  ? `${simulation.n_simulations.toLocaleString()} Monte Carlo runs`
                  : "Loading simulation preview…"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {simLoading && <PageHeaderSkeleton />}
              {simError && (
                <ErrorState
                  title="Simulation unavailable"
                  message="Start the API backend to see champion probabilities."
                />
              )}
              {topChampion && (
                <>
                  <div className="flex items-center gap-3">
                    <span className="text-4xl" aria-hidden>
                      {getTeamFlag(topChampion.team)}
                    </span>
                    <div>
                      <p className="text-2xl font-bold">{topChampion.team}</p>
                      <p className="text-sm text-muted-foreground">
                        Most likely champion
                      </p>
                    </div>
                  </div>
                  <ProbabilityBar
                    label="Win probability"
                    value={topChampion.probability}
                    color="bg-emerald-500"
                  />
                  <div className="space-y-2 pt-2">
                    {championEntries.slice(1, 4).map((entry, i) => (
                      <ProbabilityBar
                        key={entry.team}
                        label={entry.team}
                        value={entry.probability}
                        color="bg-emerald-500/70"
                        delay={0.1 * (i + 1)}
                      />
                    ))}
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </section>

        <section className="space-y-4">
          <h2 className="text-xl font-semibold">Explore</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <NavCard
              href="/groups"
              title="Groups"
              description="Official 2026 draw — 12 groups of 4 teams"
              icon={Grid3X3}
            />
            <NavCard
              href="/rankings"
              title="Rankings"
              description="ELO, model, and hybrid power rankings"
              icon={BarChart3}
              accent="from-sky-500/20 to-sky-600/5"
            />
            <NavCard
              href="/predictions"
              title="Predictions"
              description="Head-to-head win/draw/loss probabilities"
              icon={Sparkles}
              accent="from-violet-500/20 to-violet-600/5"
            />
            <NavCard
              href="/simulation"
              title="Simulation"
              description="Run full tournament Monte Carlo simulation"
              icon={Trophy}
              accent="from-amber-500/20 to-amber-600/5"
            />
          </div>
        </section>
      </div>
    </div>
  );
}
