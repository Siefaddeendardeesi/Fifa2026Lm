import { apiClient } from "./client";
import type { PredictRequest, PredictResponse } from "@/lib/types/api";

export async function predictMatch(
  request: PredictRequest
): Promise<PredictResponse> {
  const { data } = await apiClient.post<PredictResponse>("/predict", {
    home_team: request.home_team,
    away_team: request.away_team,
    neutral: request.neutral ?? true,
  });
  return data;
}
