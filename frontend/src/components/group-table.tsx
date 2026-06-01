import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getTeamFlag } from "@/lib/constants/teams";

interface GroupTableProps {
  groupName: string;
  teams: string[];
}

export function GroupTable({ groupName, teams }: GroupTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border/60">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/30 hover:bg-muted/30">
            <TableHead className="w-12 text-center">#</TableHead>
            <TableHead>Team</TableHead>
            <TableHead className="text-center">Group</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {teams.map((team, index) => (
            <TableRow key={team} className="transition-colors hover:bg-muted/20">
              <TableCell className="text-center font-medium tabular-nums text-muted-foreground">
                {index + 1}
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2.5">
                  <span className="text-xl" aria-hidden>
                    {getTeamFlag(team)}
                  </span>
                  <span className="font-medium">{team}</span>
                </div>
              </TableCell>
              <TableCell className="text-center">
                <span className="inline-flex rounded-md bg-emerald-500/10 px-2 py-0.5 text-xs font-semibold text-emerald-400">
                  {groupName}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
