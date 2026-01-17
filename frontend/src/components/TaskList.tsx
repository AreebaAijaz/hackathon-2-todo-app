"use client";

import { useState, useEffect } from "react";
import { Task } from "@/lib/types";
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
  const [filter, setFilter] = useState<"all" | "pending" | "completed">("all");
  const [deleteTarget, setDeleteTarget] = useState<Task | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const toast = useToast();

  const fetchTasks = async () => {
    try {
      const data = await api.getTasks();
      setTasks(data);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleCreate = async (title: string, description: string) => {
    try {
      const newTask = await api.createTask({ title, description });
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

  const filteredTasks = tasks.filter((task) => {
    if (filter === "pending") return !task.completed;
    if (filter === "completed") return task.completed;
    return true;
  });

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
        <button onClick={fetchTasks} className="btn btn-primary">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
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

      {/* Filter tabs */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1 p-1 bg-[var(--muted)] rounded-xl">
          {(["all", "pending", "completed"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                filter === f
                  ? "bg-[var(--card)] text-[var(--foreground)] shadow-sm"
                  : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
              {f === "all" && ` (${tasks.length})`}
              {f === "pending" && ` (${tasks.filter((t) => !t.completed).length})`}
              {f === "completed" && ` (${tasks.filter((t) => t.completed).length})`}
            </button>
          ))}
        </div>
      </div>

      {/* Task list or empty state */}
      {filteredTasks.length === 0 ? (
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
            {filter === "all"
              ? "No tasks yet"
              : filter === "pending"
              ? "No pending tasks"
              : "No completed tasks"}
          </h3>
          <p className="text-[var(--muted-foreground)] mb-6 max-w-sm mx-auto">
            {filter === "all"
              ? "Start by adding your first task. Stay organized and productive!"
              : filter === "pending"
              ? "Great job! You've completed all your tasks."
              : "Complete some tasks to see them here."}
          </p>
          {filter !== "all" && (
            <button onClick={() => setFilter("all")} className="btn btn-secondary">
              View all tasks
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTasks.map((task, index) => (
            <div key={task.id} className="stagger-item" style={{ animationDelay: `${index * 0.05}s` }}>
              <TaskItem
                task={task}
                onToggleComplete={handleToggleComplete}
                onDelete={async () => {}}
                onUpdate={handleUpdate}
                onDeleteRequest={handleDeleteRequest}
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
