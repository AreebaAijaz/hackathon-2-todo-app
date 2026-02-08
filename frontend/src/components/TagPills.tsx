"use client";

interface TagPillsProps {
  tags: string[];
  onTagClick?: (tag: string) => void;
  maxVisible?: number;
}

export default function TagPills({ tags, onTagClick, maxVisible = 5 }: TagPillsProps) {
  if (!tags || tags.length === 0) return null;

  const visible = tags.slice(0, maxVisible);
  const remaining = tags.length - maxVisible;

  return (
    <div className="flex flex-wrap gap-1">
      {visible.map((tag) => (
        <button
          key={tag}
          type="button"
          onClick={() => onTagClick?.(tag)}
          className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 hover:bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400 dark:hover:bg-blue-900/50 transition-colors cursor-pointer"
        >
          {tag}
        </button>
      ))}
      {remaining > 0 && (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400">
          +{remaining} more
        </span>
      )}
    </div>
  );
}
