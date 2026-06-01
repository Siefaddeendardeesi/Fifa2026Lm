"use client";

import { ExpandableGroupCard } from "@/components/expandable-group-card";
import { ErrorState } from "@/components/error-state";
import { GroupCardsSkeleton } from "@/components/loading-skeletons";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { GROUP_LETTERS } from "@/lib/constants/teams";
import { useGroups } from "@/lib/hooks/useGroups";

export default function GroupsPage() {
  const { data, isLoading, error } = useGroups();

  const sortedGroups = data
    ? GROUP_LETTERS.filter((letter) => data.groups[letter]).map((letter) => ({
        name: letter,
        teams: data.groups[letter] ?? [],
      }))
    : [];

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader
        badge="Group Stage"
        title="World Cup 2026 Groups"
        description="Official tournament draw — 12 groups (A–L) with 4 teams each. Click a group to expand standings."
      />

      {data && (
        <div className="flex flex-wrap gap-2">
          <Badge variant="secondary">{data.group_count} groups</Badge>
          <Badge variant="secondary">{data.team_count} teams</Badge>
        </div>
      )}

      {isLoading && <GroupCardsSkeleton />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {sortedGroups.map(({ name, teams }, index) => (
            <ExpandableGroupCard
              key={name}
              groupName={name}
              teams={teams}
              defaultOpen={index < 3}
            />
          ))}
        </div>
      )}
    </div>
  );
}
