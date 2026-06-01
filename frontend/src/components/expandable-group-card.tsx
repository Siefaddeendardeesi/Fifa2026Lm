"use client";

import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { GroupTable } from "@/components/group-table";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface ExpandableGroupCardProps {
  groupName: string;
  teams: string[];
  defaultOpen?: boolean;
}

export function ExpandableGroupCard({
  groupName,
  teams,
  defaultOpen = false,
}: ExpandableGroupCardProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <Card className="overflow-hidden border-border/60 bg-card/70 transition-colors hover:border-emerald-500/20">
      <CardHeader
        className="cursor-pointer select-none pb-3"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500/20 to-emerald-600/5 text-lg font-bold text-emerald-400">
              {groupName}
            </div>
            <div>
              <CardTitle className="text-base">Group {groupName}</CardTitle>
              <p className="text-xs text-muted-foreground">
                {teams.length} teams
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="hidden sm:inline-flex">
              {teams.slice(0, 2).join(" · ")}…
            </Badge>
            <ChevronDown
              className={cn(
                "size-4 text-muted-foreground transition-transform",
                open && "rotate-180"
              )}
            />
          </div>
        </div>
      </CardHeader>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <CardContent className="pt-0 pb-4">
              <GroupTable groupName={groupName} teams={teams} />
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}
