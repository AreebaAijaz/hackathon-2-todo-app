"use client";

import {
  Task,
  CreateTaskInput,
  UpdateTaskInput,
  TaskFilters,
  TagsResponse,
  BulkUpdateRequest,
  ChatRequest,
  ChatResponse,
  Conversation,
  ConversationDetail,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private async getAuthToken(): Promise<string | null> {
    // Get session token from Better Auth cookie
    const response = await fetch("/api/auth/get-session", {
      credentials: "include",
    });
    if (response.ok) {
      const data = await response.json();
      return data.session?.token || null;
    }
    return null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = await this.getAuthToken();

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
      credentials: "include",
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Task endpoints
  async getTasks(filters?: TaskFilters): Promise<Task[]> {
    const params = new URLSearchParams();
    if (filters) {
      if (filters.status && filters.status !== "all") params.set("status", filters.status);
      if (filters.priority) params.set("priority", filters.priority);
      if (filters.tags) params.set("tags", filters.tags);
      if (filters.due_before) params.set("due_before", filters.due_before);
      if (filters.due_after) params.set("due_after", filters.due_after);
      if (filters.overdue) params.set("overdue", "true");
      if (filters.search) params.set("search", filters.search);
      if (filters.sort_by) params.set("sort_by", filters.sort_by);
      if (filters.sort_dir) params.set("sort_dir", filters.sort_dir);
    }
    const qs = params.toString();
    return this.request<Task[]>(`/api/tasks${qs ? `?${qs}` : ""}`);
  }

  async getTags(): Promise<TagsResponse> {
    return this.request<TagsResponse>("/api/tasks/tags");
  }

  async bulkUpdate(data: BulkUpdateRequest): Promise<{ updated_count: number; task_ids: number[] }> {
    return this.request("/api/tasks/bulk", {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async createTask(data: CreateTaskInput): Promise<Task> {
    return this.request<Task>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateTask(id: number, data: UpdateTaskInput): Promise<Task> {
    return this.request<Task>(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteTask(id: number): Promise<void> {
    await this.request(`/api/tasks/${id}`, {
      method: "DELETE",
    });
  }

  async toggleComplete(id: number): Promise<Task> {
    return this.request<Task>(`/api/tasks/${id}/complete`, {
      method: "PATCH",
    });
  }

  // Chat endpoints
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>("/api/conversations");
  }

  async getConversation(id: number): Promise<ConversationDetail> {
    return this.request<ConversationDetail>(`/api/conversations/${id}`);
  }

  async deleteConversation(id: number): Promise<void> {
    await this.request(`/api/conversations/${id}`, {
      method: "DELETE",
    });
  }
}

export const api = new ApiClient();
