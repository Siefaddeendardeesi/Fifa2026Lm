"use client";

import { ErrorState } from "@/components/error-state";
import { PageHeader } from "@/components/page-header";
import { CardGridSkeleton } from "@/components/loading-skeletons";
import { TeamCard } from "@/components/team-card";
import { Badge } from "@/components/ui/badge";
import { useTeams } from "@/lib/hooks/useTeams";

export default function TeamsPage() {
  const { data, isLoading, error } = useTeams();

  const sorted = data?.teams.slice().sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader
        badge="All Nations"
        title="World Cup Teams"
        description="All 48 qualified nations for FIFA World Cup 2026 with group assignments and squad data status."
      />

      {data && (
        <Badge variant="secondary">{data.count} teams</Badge>
      )}

      {isLoading && <CardGridSkeleton count={8} />}
      {error && <ErrorState message={(error as Error).message} />}

      {sorted && (
        <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {sorted.map((team) => (
            <TeamCard key={team.name} team={team} />
          ))}
        </div>
      )}
    </div>
  );
}
