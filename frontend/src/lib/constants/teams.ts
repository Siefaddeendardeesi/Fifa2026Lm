const TEAM_FLAGS: Record<string, string> = {
  Argentina: "🇦🇷",
  Brazil: "🇧🇷",
  France: "🇫🇷",
  Germany: "🇩🇪",
  Spain: "🇪🇸",
  England: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
  Italy: "🇮🇹",
  Portugal: "🇵🇹",
  Netherlands: "🇳🇱",
  Belgium: "🇧🇪",
  Croatia: "🇭🇷",
  Uruguay: "🇺🇾",
  Colombia: "🇨🇴",
  Mexico: "🇲🇽",
  "United States": "🇺🇸",
  USA: "🇺🇸",
  Canada: "🇨🇦",
  Japan: "🇯🇵",
  "South Korea": "🇰🇷",
  Australia: "🇦🇺",
  Morocco: "🇲🇦",
  Senegal: "🇸🇳",
  Nigeria: "🇳🇬",
  Ghana: "🇬🇭",
  "Ivory Coast": "🇨🇮",
  "Côte d'Ivoire": "🇨🇮",
  Egypt: "🇪🇬",
  Tunisia: "🇹🇳",
  Algeria: "🇩🇿",
  "South Africa": "🇿🇦",
  Cameroon: "🇨🇲",
  Switzerland: "🇨🇭",
  Austria: "🇦🇹",
  Poland: "🇵🇱",
  Sweden: "🇸🇪",
  Denmark: "🇩🇰",
  Norway: "🇳🇴",
  Serbia: "🇷🇸",
  "Czech Republic": "🇨🇿",
  Czechia: "🇨🇿",
  Ukraine: "🇺🇦",
  Turkey: "🇹🇷",
  Greece: "🇬🇷",
  Wales: "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
  Scotland: "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
  "Costa Rica": "🇨🇷",
  Panama: "🇵🇦",
  Jamaica: "🇯🇲",
  Ecuador: "🇪🇨",
  Peru: "🇵🇪",
  Chile: "🇨🇱",
  Paraguay: "🇵🇾",
  Bolivia: "🇧🇴",
  Venezuela: "🇻🇪",
  Iran: "🇮🇷",
  Iraq: "🇮🇶",
  "Saudi Arabia": "🇸🇦",
  Qatar: "🇶🇦",
  "United Arab Emirates": "🇦🇪",
  UAE: "🇦🇪",
  China: "🇨🇳",
  India: "🇮🇳",
  Indonesia: "🇮🇩",
  Thailand: "🇹🇭",
  Vietnam: "🇻🇳",
  "New Zealand": "🇳🇿",
  Honduras: "🇭🇳",
  "El Salvador": "🇸🇻",
  Guatemala: "🇬🇹",
  Haiti: "🇭🇹",
  Curacao: "🇨🇼",
  Curaçao: "🇨🇼",
  "Trinidad and Tobago": "🇹🇹",
  Jordan: "🇯🇴",
  Uzbekistan: "🇺🇿",
  Oman: "🇴🇲",
  Bahrain: "🇧🇭",
  Kuwait: "🇰🇼",
};

export function getTeamFlag(team: string): string {
  return TEAM_FLAGS[team] ?? "⚽";
}

export function formatProbability(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatScore(value: number | null | undefined): string {
  if (value == null) return "—";
  return value.toFixed(1);
}

export const GROUP_LETTERS = [
  "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
] as const;

export function sortProbabilityEntries(
  entries: Record<string, number>,
  limit = 10
): Array<{ team: string; probability: number }> {
  return Object.entries(entries)
    .map(([team, probability]) => ({ team, probability }))
    .sort((a, b) => b.probability - a.probability)
    .slice(0, limit);
}

export function mergeRankings(
  elo: { team: string; score: number | null }[],
  model: { team: string; score: number | null }[],
  hybrid: { team: string; score: number | null; rank: number }[]
) {
  const teamMap = new Map<
    string,
    { team: string; elo: number | null; model: number | null; hybrid: number | null; rank: number }
  >();

  for (const entry of elo) {
    teamMap.set(entry.team, {
      team: entry.team,
      elo: entry.score,
      model: null,
      hybrid: null,
      rank: 999,
    });
  }

  for (const entry of model) {
    const existing = teamMap.get(entry.team);
    if (existing) {
      existing.model = entry.score;
    } else {
      teamMap.set(entry.team, {
        team: entry.team,
        elo: null,
        model: entry.score,
        hybrid: null,
        rank: 999,
      });
    }
  }

  for (const entry of hybrid) {
    const existing = teamMap.get(entry.team);
    if (existing) {
      existing.hybrid = entry.score;
      existing.rank = entry.rank;
    } else {
      teamMap.set(entry.team, {
        team: entry.team,
        elo: null,
        model: null,
        hybrid: entry.score,
        rank: entry.rank,
      });
    }
  }

  return Array.from(teamMap.values()).sort((a, b) => a.rank - b.rank);
}
