"use client";

import { useState, useEffect, useCallback } from "react";
import { Task, TaskFilters, CreateTaskInput } from "@/lib/types";
import { api } from "@/lib/api";
import TaskItem from "./TaskItem";
import TaskForm from "./TaskForm";
import StatsCards from "./StatsCards";
import DeleteConfirmModal from "./DeleteConfirmModal";
import { ToastContainer, useToast } from "./Toast";

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState<TaskFilters>({
    status: "all",
    sort_by: "created_at",
    sort_dir: "desc",
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Task | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const toast = useToast();

  const fetchTasks = useCallback(async (currentFilters?: TaskFilters) => {
    try {
      const f = currentFilters || filters;
      const data = await api.getTasks(f);
      setTasks(data);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchTasks();
  }, [filters]);

  // Debounced search
  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
    if (searchTimeout) clearTimeout(searchTimeout);
    const timeout = setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: query || undefined }));
    }, 300);
    setSearchTimeout(timeout);
  };

  const handleCreate = async (data: CreateTaskInput) => {
    try {
      const newTask = await api.createTask(data);
      setTasks((prev) => [newTask, ...prev]);
      toast.success("Task created successfully!");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create task");
      throw err;
    }
  };

  const handleToggleComplete = async (id: number) => {
    try {
      const updated = await api.toggleComplete(id);
      setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
      toast.success(updated.completed ? "Task completed!" : "Task reopened");
    } catch (err) {
      toast.error("Failed to update task");
      throw err;
    }
  };

  const handleDeleteRequest = (task: Task) => {
    setDeleteTarget(task);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await api.deleteTask(deleteTarget.id);
      setTasks((prev) => prev.filter((t) => t.id !== deleteTarget.id));
      toast.success("Task deleted");
      setDeleteTarget(null);
    } catch (err) {
      toast.error("Failed to delete task");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleUpdate = async (id: number, title: string, description: string) => {
    try {
      const updated = await api.updateTask(id, { title, description });
      setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
      toast.success("Task updated");
    } catch (err) {
      toast.error("Failed to update task");
      throw err;
    }
  };

  const handleTagClick = (tag: string) => {
    setFilters((prev) => ({ ...prev, tags: tag }));
  };

  const handleClearFilters = () => {
    setFilters({ status: "all", sort_by: "created_at", sort_dir: "desc" });
    setSearchQuery("");
  };

  const hasActiveFilters = !!(
    filters.priority ||
    filters.tags ||
    filters.overdue ||
    filters.search ||
    filters.sort_by !== "created_at"
  );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="relative">
          <div className="w-16 h-16 rounded-full border-4 border-[var(--muted)] border-t-[var(--gradient-start)] animate-spin" />
        </div>
        <p className="mt-4 text-[var(--muted-foreground)] font-medium">Loading your tasks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-8 text-center animate-fade-in">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--error-light)] flex items-center justify-center">
          <svg className="w-8 h-8 text-[var(--error)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold mb-2">Something went wrong</h3>
        <p className="text-[var(--muted-foreground)] mb-4">{error}</p>
        <button onClick={() => fetchTasks()} className="btn btn-primary">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <StatsCards tasks={tasks} />

      {/* Add Task Form */}
      <TaskForm onSubmit={handleCreate} />

      {/* Search bar */}
      <div className="relative">
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted-foreground)]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => handleSearchChange(e.target.value)}
          placeholder="Search tasks..."
          className="w-full pl-10 pr-10 py-2.5 bg-[var(--card)] border border-[var(--border)] rounded-xl text-sm outline-none focus:ring-2 focus:ring-[var(--gradient-start)]/20 placeholder:text-[var(--muted-foreground)]"
        />
        {searchQuery && (
          <button
            onClick={() => handleSearchChange("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Filter and Sort controls */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Status tabs */}
        <div className="flex items-center gap-1 p-1 bg-[var(--muted)] rounded-xl">
          {(["all", "pending", "completed"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilters((prev) => ({ ...prev, status: f }))}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                filters.status === f
                  ? "bg-[var(--card)] text-[var(--foreground)] shadow-sm"
                  : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        {/* Sort controls */}
        <select
          value={filters.sort_by}
          onChange={(e) =>
            setFilters((prev) => ({
              ...prev,
              sort_by: e.target.value as TaskFilters["sort_by"],
            }))
          }
          className="bg-[var(--muted)] rounded-lg px-3 py-2 text-sm outline-none"
        >
          <option value="created_at">Sort: Date Created</option>
          <option value="priority">Sort: Priority</option>
          <option value="due_date">Sort: Due Date</option>
          <option value="title">Sort: Title</option>
        </select>

        <button
          onClick={() =>
            setFilters((prev) => ({
              ...prev,
              sort_dir: prev.sort_dir === "desc" ? "asc" : "desc",
            }))
          }
          className="p-2 bg-[var(--muted)] rounded-lg hover:bg-[var(--border)] transition-colors"
          title={filters.sort_dir === "desc" ? "Descending" : "Ascending"}
        >
          <svg className={`w-4 h-4 transition-transform ${filters.sort_dir === "asc" ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Overdue toggle */}
        <button
          onClick={() =>
            setFilters((prev) => ({
              ...prev,
              overdue: prev.overdue ? undefined : true,
              status: prev.overdue ? prev.status : "pending",
            }))
          }
          className={`px-3 py-2 text-sm rounded-lg transition-all ${
            filters.overdue
              ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
              : "bg-[var(--muted)] text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
          }`}
        >
          Overdue
        </button>

        {/* Priority filter */}
        <select
          value={filters.priority || ""}
          onChange={(e) =>
            setFilters((prev) => ({
              ...prev,
              priority: e.target.value || undefined,
            }))
          }
          className="bg-[var(--muted)] rounded-lg px-3 py-2 text-sm outline-none"
        >
          <option value="">All Priorities</option>
          <option value="urgent">Urgent</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        {/* Active tag filter indicator */}
        {filters.tags && (
          <span className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-sm bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
            Tag: {filters.tags}
            <button
              onClick={() => setFilters((prev) => ({ ...prev, tags: undefined }))}
              className="hover:text-blue-900 dark:hover:text-blue-200 ml-1"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
        )}

        {/* Clear filters */}
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="px-3 py-2 text-sm text-[var(--muted-foreground)] hover:text-[var(--foreground)] underline"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Task list or empty state */}
      {tasks.length === 0 ? (
        <div className="card p-12 text-center animate-fade-in">
          <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-[var(--gradient-start)]/10 to-[var(--gradient-mid)]/10 flex items-center justify-center">
            <svg
              className="w-12 h-12 text-[var(--gradient-start)]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
              />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">
            {hasActiveFilters || filters.search
              ? "No tasks match your filters"
              : filters.status === "all"
              ? "No tasks yet"
              : filters.status === "pending"
              ? "No pending tasks"
              : "No completed tasks"}
          </h3>
          <p className="text-[var(--muted-foreground)] mb-6 max-w-sm mx-auto">
            {hasActiveFilters || filters.search
              ? "Try adjusting your filters or search query."
              : filters.status === "all"
              ? "Start by adding your first task. Stay organized and productive!"
              : filters.status === "pending"
              ? "Great job! You've completed all your tasks."
              : "Complete some tasks to see them here."}
          </p>
          {(hasActiveFilters || filters.status !== "all") && (
            <button onClick={handleClearFilters} className="btn btn-secondary">
              Clear filters
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task, index) => (
            <div key={task.id} className="stagger-item" style={{ animationDelay: `${index * 0.05}s` }}>
              <TaskItem
                task={task}
                onToggleComplete={handleToggleComplete}
                onDelete={async () => {}}
                onUpdate={handleUpdate}
                onDeleteRequest={handleDeleteRequest}
                onTagClick={handleTagClick}
              />
            </div>
          ))}
        </div>
      )}

      {/* Delete confirmation modal */}
      <DeleteConfirmModal
        isOpen={!!deleteTarget}
        taskTitle={deleteTarget?.title || ""}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteTarget(null)}
        isDeleting={isDeleting}
      />

      {/* Toast notifications */}
      <ToastContainer toasts={toast.toasts} onRemove={toast.removeToast} />
    </div>
  );
}
