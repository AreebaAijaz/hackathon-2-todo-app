"use client";

import { Priority } from "@/lib/types";

const PRIORITY_CONFIG: Record<Priority, { label: string; classes: string }> = {
  low: { label: "Low", classes: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400" },
  medium: { label: "Medium", classes: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" },
  high: { label: "High", classes: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400" },
  urgent: { label: "Urgent", classes: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" },
};

interface PriorityBadgeProps {
  priority: Priority;
}

export default function PriorityBadge({ priority }: PriorityBadgeProps) {
  const config = PRIORITY_CONFIG[priority];
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${config.classes}`}>
      {config.label}
    </span>
  );
}
