import { apiClient } from "./client";
import type { TeamsResponse } from "@/lib/types/api";

export async function fetchTeams(): Promise<TeamsResponse> {
  const { data } = await apiClient.get<TeamsResponse>("/teams");
  return data;
}
