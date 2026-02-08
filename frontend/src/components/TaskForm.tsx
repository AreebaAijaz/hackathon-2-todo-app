"use client";

import { useState, useRef } from "react";
import { Priority, RecurringPattern, CreateTaskInput } from "@/lib/types";

interface TaskFormProps {
  onSubmit: (data: CreateTaskInput) => Promise<void>;
}

export default function TaskForm({ onSubmit }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<Priority>("medium");
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [dueDate, setDueDate] = useState("");
  const [recurringPattern, setRecurringPattern] = useState<RecurringPattern>("none");
  const [isExpanded, setIsExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const titleInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        tags: tags.length > 0 ? tags : undefined,
        due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
        recurring_pattern: recurringPattern !== "none" ? recurringPattern : undefined,
      });
      setTitle("");
      setDescription("");
      setPriority("medium");
      setTags([]);
      setTagInput("");
      setDueDate("");
      setRecurringPattern("none");
      setIsExpanded(false);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !isExpanded) {
      e.preventDefault();
      handleSubmit(e);
    }
    if (e.key === "Escape") {
      setIsExpanded(false);
    }
  };

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if ((e.key === "Enter" || e.key === ",") && tagInput.trim()) {
      e.preventDefault();
      const newTag = tagInput.trim().toLowerCase().replace(/[^a-z0-9_-]/g, "");
      if (newTag && !tags.includes(newTag) && tags.length < 10) {
        setTags([...tags, newTag]);
      }
      setTagInput("");
    }
    if (e.key === "Backspace" && !tagInput && tags.length > 0) {
      setTags(tags.slice(0, -1));
    }
  };

  const removeTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag));
  };

  const priorityColors: Record<Priority, string> = {
    low: "text-gray-500",
    medium: "text-yellow-600",
    high: "text-orange-600",
    urgent: "text-red-600",
  };

  return (
    <form onSubmit={handleSubmit} className="card p-4 mb-6">
      <div className="flex items-start gap-3">
        {/* Plus icon */}
        <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center flex-shrink-0 shadow-md">
          <svg
            className="w-5 h-5 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2.5}
              d="M12 4v16m8-8H4"
            />
          </svg>
        </div>

        {/* Input area */}
        <div className="flex-1">
          <input
            ref={titleInputRef}
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onFocus={() => setIsExpanded(true)}
            onKeyDown={handleKeyDown}
            placeholder="Add a new task..."
            className="w-full bg-transparent border-none outline-none text-[15px] font-medium placeholder:text-[var(--muted-foreground)]"
            disabled={loading}
          />

          {/* Expanded form */}
          {isExpanded && (
            <div className="mt-3 animate-fade-in space-y-3">
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add a description (optional)..."
                className="w-full bg-[var(--muted)] rounded-lg px-3 py-2.5 text-sm resize-none outline-none focus:ring-2 focus:ring-[var(--gradient-start)]/20 placeholder:text-[var(--muted-foreground)]"
                rows={2}
                disabled={loading}
              />

              {/* Advanced fields row */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {/* Priority */}
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as Priority)}
                  className={`bg-[var(--muted)] rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--gradient-start)]/20 ${priorityColors[priority]}`}
                  disabled={loading}
                >
                  <option value="low">Low Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="high">High Priority</option>
                  <option value="urgent">Urgent</option>
                </select>

                {/* Due Date */}
                <input
                  type="datetime-local"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="bg-[var(--muted)] rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--gradient-start)]/20 text-[var(--foreground)]"
                  disabled={loading}
                />

                {/* Recurring */}
                <select
                  value={recurringPattern}
                  onChange={(e) => setRecurringPattern(e.target.value as RecurringPattern)}
                  className="bg-[var(--muted)] rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--gradient-start)]/20"
                  disabled={loading}
                >
                  <option value="none">No Repeat</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>

                {/* Tag input */}
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleTagKeyDown}
                  placeholder="Add tags..."
                  className="bg-[var(--muted)] rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--gradient-start)]/20 placeholder:text-[var(--muted-foreground)]"
                  disabled={loading}
                />
              </div>

              {/* Tag pills */}
              {tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => removeTag(tag)}
                        className="hover:text-blue-900 dark:hover:text-blue-200"
                      >
                        x
                      </button>
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between pt-3 border-t border-[var(--border)]">
                <p className="text-xs text-[var(--muted-foreground)]">
                  Press <kbd className="px-1.5 py-0.5 bg-[var(--muted)] rounded text-[10px] font-mono">Enter</kbd> to save,{" "}
                  <kbd className="px-1.5 py-0.5 bg-[var(--muted)] rounded text-[10px] font-mono">Esc</kbd> to cancel
                </p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setIsExpanded(false);
                      setDescription("");
                    }}
                    className="btn btn-ghost text-sm py-1.5"
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading || !title.trim()}
                    className="btn btn-primary text-sm py-1.5"
                  >
                    {loading ? (
                      <>
                        <div className="spinner w-4 h-4" />
                        Adding...
                      </>
                    ) : (
                      <>
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 4v16m8-8H4"
                          />
                        </svg>
                        Add Task
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Quick add button (when not expanded) */}
        {!isExpanded && title.trim() && (
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary text-sm py-2 animate-fade-in"
          >
            {loading ? (
              <div className="spinner w-4 h-4" />
            ) : (
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
            )}
          </button>
        )}
      </div>
    </form>
  );
}
