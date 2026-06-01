"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Play, Trophy } from "lucide-react";
import { Bracket } from "@/components/bracket";
import { ErrorState } from "@/components/error-state";
import { PageHeader } from "@/components/page-header";
import { ProbabilityBar } from "@/components/probability-bar";
import { SimulationSkeleton } from "@/components/loading-skeletons";
import { Badge } from "@/components/ui/badge";
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
import { getTeamFlag, sortProbabilityEntries } from "@/lib/constants/teams";
import { useSimulate } from "@/lib/hooks/useSimulate";

const SIM_OPTIONS = [
  { value: "200", label: "200 runs (fast)" },
  { value: "500", label: "500 runs (default)" },
  { value: "1000", label: "1,000 runs (accurate)" },
  { value: "2000", label: "2,000 runs (precise)" },
];

export default function SimulationPage() {
  const simulate = useSimulate();
  const [nSims, setNSims] = useState("500");

  const championEntries = simulate.data
    ? sortProbabilityEntries(simulate.data.champion_probability, 12)
    : [];
  const finalistEntries = simulate.data
    ? sortProbabilityEntries(simulate.data.finalist_probability, 12)
    : [];

  function handleRun() {
    simulate.mutate({ n_simulations: parseInt(nSims, 10), seed: 42 });
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader
        badge="Monte Carlo"
        title="World Cup Simulation"
        description="Run thousands of full tournament simulations to estimate champion, finalist, and group winner probabilities."
      />

      <Card className="border-border/60 bg-card/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="size-5 text-emerald-400" />
            Tournament Simulator
          </CardTitle>
          <CardDescription>
            Each run simulates the full group stage and knockout rounds
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-end">
          <div className="space-y-2 sm:w-56">
            <label className="text-sm font-medium">Simulations</label>
            <Select value={nSims} onValueChange={(v) => setNSims(v ?? "500")}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SIM_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button
            size="lg"
            onClick={handleRun}
            disabled={simulate.isPending}
            className="gap-2"
          >
            {simulate.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Play className="size-4" />
            )}
            Run World Cup Simulation
          </Button>
        </CardContent>
      </Card>

      <AnimatePresence>
        {simulate.isPending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Card className="border-emerald-500/20 bg-emerald-500/5">
              <CardContent className="flex flex-col items-center gap-4 py-12">
                <div className="relative">
                  <Loader2 className="size-12 animate-spin text-emerald-400" />
                  <motion.div
                    className="absolute inset-0 rounded-full border-2 border-emerald-500/30"
                    animate={{ scale: [1, 1.4, 1], opacity: [0.6, 0, 0.6] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  />
                </div>
                <div className="text-center">
                  <p className="font-semibold">Running Monte Carlo simulation…</p>
                  <p className="text-sm text-muted-foreground">
                    Simulating {parseInt(nSims, 10).toLocaleString()} tournament
                    outcomes
                  </p>
                </div>
                <div className="flex gap-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <motion.span
                      key={i}
                      className="text-2xl"
                      animate={{ y: [0, -8, 0] }}
                      transition={{
                        duration: 0.6,
                        repeat: Infinity,
                        delay: i * 0.1,
                      }}
                    >
                      ⚽
                    </motion.span>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {simulate.isPending && !simulate.data && <SimulationSkeleton />}
      {simulate.error && (
        <ErrorState message={(simulate.error as Error).message} />
      )}

      {simulate.data && !simulate.isPending && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary">
              {simulate.data.n_simulations.toLocaleString()} simulations
            </Badge>
            <Badge variant="secondary">Seed {simulate.data.seed}</Badge>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="border-border/60 bg-card/70">
              <CardHeader>
                <CardTitle>Champion Probabilities</CardTitle>
                <CardDescription>
                  Likelihood of winning the World Cup
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {championEntries.map((entry, i) => (
                  <div key={entry.team} className="flex items-center gap-3">
                    <span className="w-6 text-lg" aria-hidden>
                      {getTeamFlag(entry.team)}
                    </span>
                    <div className="flex-1">
                      <ProbabilityBar
                        label={entry.team}
                        value={entry.probability}
                        color={
                          i === 0
                            ? "bg-emerald-500"
                            : i < 3
                              ? "bg-emerald-500/70"
                              : "bg-muted-foreground/50"
                        }
                        delay={i * 0.05}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="border-border/60 bg-card/70">
              <CardHeader>
                <CardTitle>Finalist Probabilities</CardTitle>
                <CardDescription>
                  Teams most likely to reach the final
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {finalistEntries.slice(0, 10).map((entry, i) => (
                  <div key={entry.team} className="flex items-center gap-3">
                    <span className="w-6 text-lg" aria-hidden>
                      {getTeamFlag(entry.team)}
                    </span>
                    <div className="flex-1">
                      <ProbabilityBar
                        label={entry.team}
                        value={entry.probability}
                        color="bg-sky-500"
                        delay={i * 0.05}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <Card className="border-border/60 bg-card/70">
            <CardHeader>
              <CardTitle>Knockout Outlook</CardTitle>
              <CardDescription>
                Semi-final contenders, finalists, and champion favorites
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Bracket
                champion={championEntries.map((e) => ({
                  team: e.team,
                  probability: e.probability,
                }))}
                finalists={finalistEntries.map((e) => ({
                  team: e.team,
                  probability: e.probability,
                }))}
              />
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
