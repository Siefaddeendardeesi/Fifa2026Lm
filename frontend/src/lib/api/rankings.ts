import { apiClient } from "./client";
import type { RankingMethod, RankingsResponse } from "@/lib/types/api";

export interface RankingsParams {
  method?: RankingMethod;
  since?: string;
  pool_size?: number;
}

export async function fetchRankings(
  params: RankingsParams = {}
): Promise<RankingsResponse> {
  const { data } = await apiClient.get<RankingsResponse>("/rankings", {
    params: {
      method: params.method ?? "model",
      since: params.since ?? "2024-01-01",
      pool_size: params.pool_size ?? 48,
    },
  });
  return data;
}

export async function fetchAllRankings(
  poolSize = 48
): Promise<Record<RankingMethod, RankingsResponse>> {
  const methods: RankingMethod[] = ["elo", "model", "hybrid"];
  const results = await Promise.all(
    methods.map((method) => fetchRankings({ method, pool_size: poolSize }))
  );
  return {
    elo: results[0],
    model: results[1],
    hybrid: results[2],
  };
}
