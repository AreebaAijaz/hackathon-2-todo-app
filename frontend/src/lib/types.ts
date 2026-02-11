/**
 * Shared TypeScript types for the Todo application.
 */

export type Priority = "low" | "medium" | "high" | "urgent";
export type RecurringPattern = "none" | "daily" | "weekly" | "monthly";

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  priority: Priority;
  tags: string[];
  due_date: string | null;
  recurring_pattern: RecurringPattern;
  is_overdue: boolean;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  priority?: Priority;
  tags?: string[];
  due_date?: string | null;
  recurring_pattern?: RecurringPattern;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  priority?: Priority;
  tags?: string[];
  due_date?: string | null;
  recurring_pattern?: RecurringPattern;
}

export interface TaskFilters {
  status?: "all" | "pending" | "completed";
  priority?: string;
  tags?: string;
  due_before?: string;
  due_after?: string;
  overdue?: boolean;
  search?: string;
  sort_by?: "created_at" | "due_date" | "priority" | "title";
  sort_dir?: "asc" | "desc";
}

export interface BulkUpdateRequest {
  task_ids: number[];
  operations: {
    priority?: Priority;
    add_tags?: string[];
    remove_tags?: string[];
    due_date?: string | null;
    recurring_pattern?: RecurringPattern;
  };
}

export interface TagsResponse {
  tags: string[];
  count: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface ApiError {
  detail: string;
}

// Chat types
export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail {
  id: number;
  title: string | null;
  created_at: string;
  messages: ChatMessage[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ChatResponse {
  response: string;
  conversation_id: number;
  message_id: number;
  agent_used: string | null;
}
