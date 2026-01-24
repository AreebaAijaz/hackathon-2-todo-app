"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useSession } from "@/lib/auth-client";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

interface Conversation {
  id: number;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface ChatKitWindowProps {
  className?: string;
}

export default function ChatKitWindow({ className = "" }: ChatKitWindowProps) {
  const { data: session } = useSession();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Get auth token for API requests
  const getAuthToken = async (): Promise<string | null> => {
    try {
      const response = await fetch("/api/auth/get-session", {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        return data.session?.session?.token || null;
      }
    } catch (e) {
      console.error("Failed to get auth token:", e);
    }
    return null;
  };

  // Load conversations list
  const loadConversations = useCallback(async () => {
    const token = await getAuthToken();
    if (!token) return;

    setLoadingConversations(true);
    try {
      const response = await fetch(`${apiUrl}/api/conversations`, {
        headers: { Authorization: `Bearer ${token}` },
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (e) {
      console.error("Failed to load conversations:", e);
    } finally {
      setLoadingConversations(false);
    }
  }, [apiUrl]);

  // Load a specific conversation
  const loadConversation = async (conversationId: number) => {
    const token = await getAuthToken();
    if (!token) return;

    try {
      const response = await fetch(`${apiUrl}/api/conversations/${conversationId}`, {
        headers: { Authorization: `Bearer ${token}` },
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentConversationId(conversationId);
        setMessages(
          data.messages.map((m: { id: number; role: string; content: string }) => ({
            id: `msg-${m.id}`,
            role: m.role as "user" | "assistant",
            content: m.content,
          }))
        );
      }
    } catch (e) {
      console.error("Failed to load conversation:", e);
    }
  };

  // Delete a conversation
  const deleteConversation = async (conversationId: number) => {
    const token = await getAuthToken();
    if (!token) return;

    try {
      const response = await fetch(`${apiUrl}/api/conversations/${conversationId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
        credentials: "include",
      });
      if (response.ok) {
        setConversations((prev) => prev.filter((c) => c.id !== conversationId));
        if (currentConversationId === conversationId) {
          startNewChat();
        }
      }
    } catch (e) {
      console.error("Failed to delete conversation:", e);
    }
  };

  // Start a new chat
  const startNewChat = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setError(null);
  };

  // Load conversations on mount
  useEffect(() => {
    if (session) {
      loadConversations();
    }
  }, [session, loadConversations]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  const sendMessage = useCallback(async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    setError(null);
    setIsLoading(true);

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: messageText,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    // Create placeholder for assistant message
    const assistantId = `assistant-${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      isStreaming: true,
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      // Get auth token
      const token = await getAuthToken();
      if (!token) {
        throw new Error("Not authenticated. Please sign in again.");
      }

      // Build conversation history
      const conversationHistory = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await fetch(`${apiUrl}/api/chatkit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        credentials: "include",
        body: JSON.stringify({
          message: messageText,
          conversation_history: conversationHistory,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Read SSE stream
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();
      let accumulatedContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === "response.output_text.delta" && data.delta) {
                accumulatedContent += data.delta;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId
                      ? { ...m, content: accumulatedContent }
                      : m
                  )
                );
              } else if (data.type === "response.output_text.done") {
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId
                      ? { ...m, content: data.text || accumulatedContent, isStreaming: false }
                      : m
                  )
                );
              } else if (data.type === "error") {
                throw new Error(data.error?.message || "Unknown error");
              }
            } catch {
              // Ignore JSON parse errors for incomplete chunks
            }
          }
        }
      }

      // Ensure streaming is marked complete
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId ? { ...m, isStreaming: false } : m
        )
      );

      // Refresh conversations list to show new/updated conversation
      loadConversations();

    } catch (err) {
      console.error("Chat error:", err);
      setError(err instanceof Error ? err.message : "Failed to send message");
      // Remove the assistant message on error
      setMessages((prev) => prev.filter((m) => m.id !== assistantId));
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, messages, apiUrl, loadConversations]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  if (!session) {
    return (
      <div className="h-full flex items-center justify-center bg-[var(--background)]">
        <p className="text-[var(--muted-foreground)]">Please sign in to chat</p>
      </div>
    );
  }

  return (
    <div className={`flex h-full bg-[var(--background)] ${className}`}>
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "w-72" : "w-0"
        } transition-all duration-300 overflow-hidden border-r border-[var(--border)] bg-[var(--card)] flex flex-col`}
      >
        {/* Sidebar Header */}
        <div className="p-3 border-b border-[var(--border)]">
          <button
            onClick={startNewChat}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-[var(--border)] hover:bg-[var(--muted)] transition-colors text-sm font-medium"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto p-2">
          {loadingConversations ? (
            <div className="flex justify-center py-4">
              <div className="w-5 h-5 border-2 border-[var(--muted)] border-t-[var(--gradient-start)] rounded-full animate-spin" />
            </div>
          ) : conversations.length === 0 ? (
            <p className="text-center text-sm text-[var(--muted-foreground)] py-4">
              No conversations yet
            </p>
          ) : (
            <div className="space-y-1">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                    currentConversationId === conv.id
                      ? "bg-[var(--muted)]"
                      : "hover:bg-[var(--muted)]/50"
                  }`}
                  onClick={() => loadConversation(conv.id)}
                >
                  <svg className="w-4 h-4 text-[var(--muted-foreground)] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <span className="flex-1 text-sm truncate">
                    {conv.title || "New conversation"}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConversation(conv.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-[var(--border)] transition-all"
                    title="Delete conversation"
                  >
                    <svg className="w-3.5 h-3.5 text-[var(--muted-foreground)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat Header */}
        <div className="flex items-center gap-3 px-4 py-2 border-b border-[var(--border)] bg-[var(--card)]">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-[var(--muted)] transition-colors"
            title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h2 className="font-medium truncate">
            {currentConversationId
              ? conversations.find((c) => c.id === currentConversationId)?.title || "Chat"
              : "New Chat"}
          </h2>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center px-4">
              <div className="w-20 h-20 rounded-2xl gradient-bg flex items-center justify-center mb-6 shadow-lg">
                <svg
                  className="w-10 h-10 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold mb-2">AI Task Assistant</h2>
              <p className="text-[var(--muted-foreground)] max-w-md mb-8">
                I can help you manage your tasks. Try one of these:
              </p>
              <div className="grid grid-cols-2 gap-3 max-w-lg">
                {[
                  { text: "Add a task to buy groceries", icon: "+" },
                  { text: "Show all my tasks", icon: "📋" },
                  { text: "What tasks are pending?", icon: "⏳" },
                  { text: "Mark groceries as done", icon: "✓" },
                ].map((suggestion) => (
                  <button
                    key={suggestion.text}
                    onClick={() => sendMessage(suggestion.text)}
                    className="flex items-center gap-2 px-4 py-3 text-sm text-left bg-[var(--card)] hover:bg-[var(--muted)] border border-[var(--border)] rounded-xl transition-colors"
                  >
                    <span className="text-lg">{suggestion.icon}</span>
                    <span>{suggestion.text}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                      message.role === "user"
                        ? "bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-mid)] text-white rounded-br-sm"
                        : "bg-[var(--card)] border border-[var(--border)] rounded-bl-sm"
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
                      {message.content}
                      {message.isStreaming && (
                        <span className="inline-block w-2 h-5 ml-1 bg-current animate-pulse rounded-sm" />
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
                <div className="flex justify-start">
                  <div className="bg-[var(--card)] border border-[var(--border)] rounded-2xl rounded-bl-sm px-4 py-3">
                    <div className="flex gap-1.5">
                      <span className="w-2 h-2 bg-[var(--muted-foreground)] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="w-2 h-2 bg-[var(--muted-foreground)] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="w-2 h-2 bg-[var(--muted-foreground)] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Error message */}
        {error && (
          <div className="mx-4 mb-2 p-3 bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 rounded-lg text-sm border border-red-200 dark:border-red-900">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
          </div>
        )}

        {/* Input area */}
        <div className="border-t border-[var(--border)] bg-[var(--card)] p-4">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="flex gap-3 items-end">
              <div className="flex-1 relative">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask me to add, list, or complete tasks..."
                  disabled={isLoading}
                  rows={1}
                  className="w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-[15px] placeholder:text-[var(--muted-foreground)] focus:outline-none focus:ring-2 focus:ring-[var(--gradient-start)] focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-shadow"
                  style={{ minHeight: "48px", maxHeight: "150px" }}
                />
              </div>
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="h-12 px-5 rounded-xl gradient-bg text-white font-medium hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-md hover:shadow-lg"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                    />
                  </svg>
                )}
                <span className="hidden sm:inline">Send</span>
              </button>
            </div>
            <p className="text-xs text-[var(--muted-foreground)] mt-2 text-center">
              Press Enter to send, Shift+Enter for new line
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
