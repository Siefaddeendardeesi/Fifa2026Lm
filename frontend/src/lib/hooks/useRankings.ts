"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchAllRankings, fetchRankings } from "@/lib/api/rankings";
import type { RankingMethod } from "@/lib/types/api";
import { mergeRankings } from "@/lib/constants/teams";

export function useRankings(method: RankingMethod = "hybrid", poolSize = 48) {
  return useQuery({
    queryKey: ["rankings", method, poolSize],
    queryFn: () => fetchRankings({ method, pool_size: poolSize }),
    staleTime: 2 * 60 * 1000,
  });
}

export function useMergedRankings(poolSize = 48) {
  return useQuery({
    queryKey: ["rankings", "merged", poolSize],
    queryFn: async () => {
      const all = await fetchAllRankings(poolSize);
      return mergeRankings(
        all.elo.rankings.map((r) => ({ team: r.team, score: r.elo ?? r.score })),
        all.model.rankings.map((r) => ({ team: r.team, score: r.score })),
        all.hybrid.rankings.map((r) => ({
          team: r.team,
          score: r.score,
          rank: r.rank,
        }))
      );
    },
    staleTime: 2 * 60 * 1000,
  });
}
