import { Card } from "@/components/ui/card";
import { MessageSquare, TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { DashboardStats } from "../types";

interface StatCardsProps {
  stats: DashboardStats;
}

export function StatCards({ stats }: StatCardsProps) {
  const items = [
    {
      key: "total",
      label: "Total Feedback",
      value: stats.total_feedback,
      valueClass: "",
      Icon: MessageSquare,
      iconClass: "text-muted-foreground",
    },
    {
      key: "positive",
      label: "Positive",
      value: stats.sentiment_breakdown.positive || 0,
      valueClass: "text-green-600",
      Icon: TrendingUp,
      iconClass: "text-green-600",
    },
    {
      key: "neutral",
      label: "Neutral",
      value: stats.sentiment_breakdown.neutral || 0,
      valueClass: "text-gray-600",
      Icon: Minus,
      iconClass: "text-gray-600",
    },
    {
      key: "negative",
      label: "Negative",
      value: stats.sentiment_breakdown.negative || 0,
      valueClass: "text-red-600",
      Icon: TrendingDown,
      iconClass: "text-red-600",
    },
  ];

  return (
    <>
      {items.map(({ key, label, value, valueClass, Icon, iconClass }) => (
        <Card key={key} className="p-4 shadow-none">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                {label}
              </p>
              <p className={`text-2xl font-bold ${valueClass}`}>{value}</p>
            </div>
            <Icon className={`h-5 w-5 ${iconClass}`} />
          </div>
        </Card>
      ))}
    </>
  );
}
