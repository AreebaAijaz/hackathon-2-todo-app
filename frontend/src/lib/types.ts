/**
 * Shared TypeScript types for the Todo application.
 */

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface ApiError {
  detail: string;
}
