import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface NavCardProps {
  href: string;
  title: string;
  description: string;
  icon: LucideIcon;
  accent?: string;
}

export function NavCard({
  href,
  title,
  description,
  icon: Icon,
  accent = "from-emerald-500/20 to-emerald-600/5",
}: NavCardProps) {
  return (
    <Link href={href} className="group block h-full">
      <Card className="h-full border-border/60 bg-card/60 transition-all duration-300 hover:-translate-y-1 hover:border-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/10">
        <CardHeader>
          <div
            className={cn(
              "mb-3 flex size-11 items-center justify-center rounded-xl bg-gradient-to-br",
              accent
            )}
          >
            <Icon className="size-5 text-emerald-400" />
          </div>
          <CardTitle className="text-lg group-hover:text-emerald-400 transition-colors">
            {title}
          </CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
      </Card>
    </Link>
  );
}
