"use client";

interface DueDateDisplayProps {
  due_date: string | null;
  completed: boolean;
}

export default function DueDateDisplay({ due_date, completed }: DueDateDisplayProps) {
  if (!due_date) return null;

  const date = new Date(due_date);
  const now = new Date();
  const isOverdue = date < now && !completed;

  const formatDueDate = () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const dueDay = new Date(date);
    dueDay.setHours(0, 0, 0, 0);
    const diffDays = Math.round((dueDay.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Tomorrow";
    if (diffDays === -1) return "Yesterday";
    if (diffDays > 1 && diffDays <= 7) return `In ${diffDays} days`;
    if (diffDays < -1 && diffDays >= -7) return `${Math.abs(diffDays)} days ago`;
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  return (
    <span
      className={`inline-flex items-center gap-1 text-xs ${
        isOverdue
          ? "text-red-600 dark:text-red-400 font-medium"
          : "text-[var(--muted-foreground)]"
      }`}
    >
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
      </svg>
      {isOverdue && "Overdue: "}
      {formatDueDate()}
    </span>
  );
}
