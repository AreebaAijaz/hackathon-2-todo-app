"use client";

import { useState, useRef } from "react";

interface TaskFormProps {
  onSubmit: (title: string, description: string) => Promise<void>;
}

export default function TaskForm({ onSubmit }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const titleInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);

    try {
      await onSubmit(title.trim(), description.trim());
      setTitle("");
      setDescription("");
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
      setDescription("");
    }
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
            <div className="mt-3 animate-fade-in">
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Add a description (optional)..."
                className="w-full bg-[var(--muted)] rounded-lg px-3 py-2.5 text-sm resize-none outline-none focus:ring-2 focus:ring-[var(--gradient-start)]/20 placeholder:text-[var(--muted-foreground)]"
                rows={2}
                disabled={loading}
              />

              <div className="flex items-center justify-between mt-3 pt-3 border-t border-[var(--border)]">
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
