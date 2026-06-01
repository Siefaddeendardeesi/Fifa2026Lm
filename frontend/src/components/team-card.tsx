import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getTeamFlag } from "@/lib/constants/teams";
import type { TeamInfo } from "@/lib/types/api";

interface TeamCardProps {
  team: TeamInfo;
  rank?: number;
  score?: number | null;
  href?: string;
}

export function TeamCard({ team, rank, score, href }: TeamCardProps) {
  const content = (
    <Card className="group h-full border-border/60 bg-card/70 transition-all hover:border-emerald-500/40 hover:bg-card hover:shadow-lg hover:shadow-emerald-500/5">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <span className="text-3xl" aria-hidden>
            {getTeamFlag(team.name)}
          </span>
          {rank != null && (
            <Badge variant="outline" className="tabular-nums">
              #{rank}
            </Badge>
          )}
        </div>
        <CardTitle className="text-base leading-tight">{team.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 pt-0">
        {team.group && (
          <Badge variant="secondary">Group {team.group}</Badge>
        )}
        {score != null && (
          <p className="text-sm text-muted-foreground">
            Score: <span className="font-medium text-foreground">{score.toFixed(1)}</span>
          </p>
        )}
        {team.has_squad && (
          <p className="text-xs text-emerald-500">Squad data available</p>
        )}
      </CardContent>
    </Card>
  );

  if (href) {
    return (
      <Link href={href} className="block h-full">
        {content}
      </Link>
    );
  }

  return content;
}
