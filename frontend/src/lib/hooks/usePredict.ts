"use client";

import { useMutation } from "@tanstack/react-query";
import { predictMatch } from "@/lib/api/predictions";
import type { PredictRequest } from "@/lib/types/api";

export function usePredict() {
  return useMutation({
    mutationFn: (request: PredictRequest) => predictMatch(request),
  });
}
