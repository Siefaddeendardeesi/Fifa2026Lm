export interface PredictRequest {
  home_team: string;
  away_team: string;
  neutral?: boolean;
}

export interface PredictResponse {
  home_team: string;
  away_team: string;
  home_win: number;
  draw: number;
  away_win: number;
  confidence: number;
}

export interface SimulateRequest {
  n_simulations?: number;
  seed?: number;
}

export interface SimulateResponse {
  n_simulations: number;
  seed: number;
  champion_probability: Record<string, number>;
  finalist_probability: Record<string, number>;
  group_winner_probability: Record<string, Record<string, number>>;
}

export type RankingMethod = "elo" | "model" | "hybrid";

export interface RankingEntry {
  rank: number;
  team: string;
  score: number | null;
  avg_win_prob: number | null;
  elo: number | null;
  fifa_rank: number | null;
}

export interface RankingsResponse {
  method: RankingMethod;
  pool_size: number;
  rankings: RankingEntry[];
}

export interface TeamInfo {
  name: string;
  group: string | null;
  has_squad: boolean;
}

export interface TeamsResponse {
  teams: TeamInfo[];
  count: number;
}

export interface GroupsResponse {
  groups: Record<string, string[]>;
  group_count: number;
  team_count: number;
}

export interface ApiError {
  error: string;
  details?: Record<string, unknown>;
}

export interface MergedRankingRow {
  rank: number;
  team: string;
  elo: number | null;
  model: number | null;
  hybrid: number | null;
}
