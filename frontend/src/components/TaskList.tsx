"use client";

import { useState, useEffect } from "react";
import { Task } from "@/lib/types";
import { api } from "@/lib/api";
import TaskItem from "./TaskItem";
import TaskForm from "./TaskForm";

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
    const newTask = await api.createTask({ title, description });
    setTasks((prev) => [newTask, ...prev]);
  };

  const handleToggleComplete = async (id: number) => {
    const updated = await api.toggleComplete(id);
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? updated : t))
    );
  };

  const handleDelete = async (id: number) => {
    await api.deleteTask(id);
    setTasks((prev) => prev.filter((t) => t.id !== id));
  };

  const handleUpdate = async (id: number, title: string, description: string) => {
    const updated = await api.updateTask(id, { title, description });
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? updated : t))
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded-lg text-center">
        <p>{error}</p>
        <button
          onClick={fetchTasks}
          className="mt-2 text-sm underline hover:no-underline"
        >
          Try again
        </button>
      </div>
    );
  }

  const completedCount = tasks.filter((t) => t.completed).length;

  return (
    <div className="space-y-6">
      <TaskForm onSubmit={handleCreate} />

      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>{tasks.length} tasks</span>
        <span>{completedCount} completed</span>
      </div>

      {tasks.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">No tasks yet</p>
          <p className="text-sm mt-1">Add a task to get started!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggleComplete={handleToggleComplete}
              onDelete={handleDelete}
              onUpdate={handleUpdate}
            />
          ))}
        </div>
      )}
    </div>
  );
}
