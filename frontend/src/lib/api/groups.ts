import { apiClient } from "./client";
import type { GroupsResponse } from "@/lib/types/api";

export async function fetchGroups(): Promise<GroupsResponse> {
  const { data } = await apiClient.get<GroupsResponse>("/groups");
  return data;
}
