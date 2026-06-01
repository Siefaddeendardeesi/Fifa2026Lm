import { apiClient } from "./client";
import type { SimulateRequest, SimulateResponse } from "@/lib/types/api";

export async function runSimulation(
  request: SimulateRequest = {}
): Promise<SimulateResponse> {
  const { data } = await apiClient.post<SimulateResponse>("/simulate", {
    n_simulations: request.n_simulations ?? 500,
    seed: request.seed ?? 42,
  });
  return data;
}
