"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { runSimulation } from "@/lib/api/simulation";
import type { SimulateRequest } from "@/lib/types/api";

export function useSimulate() {
  return useMutation({
    mutationFn: (request: SimulateRequest = {}) => runSimulation(request),
  });
}

export function useSimulationPreview(enabled = true) {
  return useQuery({
    queryKey: ["simulation", "preview"],
    queryFn: () => runSimulation({ n_simulations: 200, seed: 42 }),
    staleTime: 10 * 60 * 1000,
    enabled,
    retry: 1,
  });
}
