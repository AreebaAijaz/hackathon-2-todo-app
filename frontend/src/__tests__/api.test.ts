import { api } from "../lib/api";
import {
  Task,
  CreateTaskInput,
  UpdateTaskInput,
  ChatRequest,
  ChatResponse,
  Conversation,
  ConversationDetail,
} from "../lib/types";

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch as any;

describe("ApiClient", () => {
  beforeEach(() => {
    // Clear all mocks before each test
    mockFetch.mockClear();
  });

  // Helper to mock auth token retrieval
  const mockAuthToken = (token: string | null) => {
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            session: {
              session: { token },
              user: { id: "user-123" },
            },
          }),
      })
    );
  };

  describe("getTasks", () => {
    it("should call correct endpoint and return tasks", async () => {
      const mockTasks: Task[] = [
        {
          id: 1,
          user_id: "user-123",
          title: "Test Task 1",
          description: "Description 1",
          completed: false,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T00:00:00Z",
        },
        {
          id: 2,
          user_id: "user-123",
          title: "Test Task 2",
          description: "Description 2",
          completed: true,
          created_at: "2024-01-02T00:00:00Z",
          updated_at: "2024-01-02T00:00:00Z",
        },
      ];

      // Mock auth token fetch
      mockAuthToken("test-token-123");

      // Mock the actual API call
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTasks),
        })
      );

      const result = await api.getTasks();

      expect(result).toEqual(mockTasks);
      expect(mockFetch).toHaveBeenCalledTimes(2); // Once for auth, once for API
      expect(mockFetch).toHaveBeenLastCalledWith(
        "http://localhost:8000/api/tasks",
        expect.objectContaining({
          headers: expect.objectContaining({
            "Content-Type": "application/json",
            Authorization: "Bearer test-token-123",
          }),
          credentials: "include",
        })
      );
    });
  });

  describe("createTask", () => {
    it("should send POST with correct body", async () => {
      const input: CreateTaskInput = {
        title: "New Task",
        description: "New Description",
      };

      const mockTask: Task = {
        id: 3,
        user_id: "user-123",
        title: "New Task",
        description: "New Description",
        completed: false,
        created_at: "2024-01-03T00:00:00Z",
        updated_at: "2024-01-03T00:00:00Z",
      };

      mockAuthToken("test-token-123");

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTask),
        })
      );

      const result = await api.createTask(input);

      expect(result).toEqual(mockTask);
      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(mockFetch).toHaveBeenLastCalledWith(
        "http://localhost:8000/api/tasks",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify(input),
          headers: expect.objectContaining({
            "Content-Type": "application/json",
            Authorization: "Bearer test-token-123",
          }),
        })
      );
    });
  });

  describe("updateTask", () => {
    it("should send PUT with correct body", async () => {
      const taskId = 1;
      const input: UpdateTaskInput = {
        title: "Updated Task",
      };

      const mockTask: Task = {
        id: taskId,
        user_id: "user-123",
        title: "Updated Task",
        description: "Original Description",
        completed: false,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-03T00:00:00Z",
      };

      mockAuthToken("test-token-123");

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTask),
        })
      );

      const result = await api.updateTask(taskId, input);

      expect(result).toEqual(mockTask);
      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(mockFetch).toHaveBeenLastCalledWith(
        `http://localhost:8000/api/tasks/${taskId}`,
        expect.objectContaining({
          method: "PUT",
          body: JSON.stringify(input),
        })
      );
    });
  });

  describe("deleteTask", () => {
    it("should send DELETE to correct URL", async () => {
      const taskId = 1;

      mockAuthToken("test-token-123");

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({}),
        })
      );

      await api.deleteTask(taskId);

      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(mockFetch).toHaveBeenLastCalledWith(
        `http://localhost:8000/api/tasks/${taskId}`,
        expect.objectContaining({
          method: "DELETE",
        })
      );
    });
  });

  describe("toggleComplete", () => {
    it("should send PATCH to toggle task completion", async () => {
      const taskId = 1;
      const mockTask: Task = {
        id: taskId,
        user_id: "user-123",
        title: "Test Task",
        description: "Description",
        completed: true,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-03T00:00:00Z",
      };

      mockAuthToken("test-token-123");

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTask),
        })
      );

      const result = await api.toggleComplete(taskId);

      expect(result).toEqual(mockTask);
      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(mockFetch).toHaveBeenLastCalledWith(
        `http://localhost:8000/api/tasks/${taskId}/complete`,
        expect.objectContaining({
          method: "PATCH",
        })
      );
    });
  });

  describe("API error handling", () => {
    it("should throw error on non-ok response", async () => {
      mockAuthToken("test-token-123");

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: false,
          status: 404,
          json: () => Promise.resolve({ detail: "Task not found" }),
        })
      );

      await expect(api.getTasks()).rejects.toThrow("Task not found");
    });

    it("should throw generic error when response has no detail", async () => {
      mockAuthToken("test-token-123");

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          json: () => Promise.reject(new Error("Invalid JSON")),
        })
      );

      await expect(api.getTasks()).rejects.toThrow("Request failed");
    });

    it("should handle unauthorized errors", async () => {
      mockAuthToken("test-token-123");

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: false,
          status: 401,
          json: () => Promise.resolve({ detail: "Authentication required" }),
        })
      );

      await expect(api.getTasks()).rejects.toThrow("Authentication required");
    });
  });

  describe("Chat endpoints", () => {
    describe("sendMessage", () => {
      it("should send chat message with conversation_id", async () => {
        const request: ChatRequest = {
          message: "What are my tasks?",
          conversation_id: 42,
        };

        const response: ChatResponse = {
          reply: "You have 3 tasks.",
          conversation_id: 42,
        };

        mockAuthToken("test-token-123");

        mockFetch.mockImplementationOnce(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(response),
          })
        );

        const result = await api.sendMessage(request);

        expect(result).toEqual(response);
        expect(mockFetch).toHaveBeenLastCalledWith(
          "http://localhost:8000/api/chat",
          expect.objectContaining({
            method: "POST",
            body: JSON.stringify(request),
          })
        );
      });

      it("should send chat message without conversation_id", async () => {
        const request: ChatRequest = {
          message: "Create a new task",
        };

        const response: ChatResponse = {
          reply: "Task created successfully.",
          conversation_id: 43,
        };

        mockAuthToken("test-token-123");

        mockFetch.mockImplementationOnce(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(response),
          })
        );

        const result = await api.sendMessage(request);

        expect(result).toEqual(response);
        expect(result.conversation_id).toBe(43);
      });
    });

    describe("getConversations", () => {
      it("should fetch all conversations", async () => {
        const mockConversations: Conversation[] = [
          {
            id: 1,
            user_id: "user-123",
            title: "Task Management",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
          {
            id: 2,
            user_id: "user-123",
            title: null,
            created_at: "2024-01-02T00:00:00Z",
            updated_at: "2024-01-02T00:00:00Z",
          },
        ];

        mockAuthToken("test-token-123");

        mockFetch.mockImplementationOnce(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockConversations),
          })
        );

        const result = await api.getConversations();

        expect(result).toEqual(mockConversations);
        expect(mockFetch).toHaveBeenLastCalledWith(
          "http://localhost:8000/api/conversations",
          expect.any(Object)
        );
      });
    });

    describe("getConversation", () => {
      it("should fetch conversation detail with messages", async () => {
        const mockConversationDetail: ConversationDetail = {
          id: 1,
          user_id: "user-123",
          title: "Task Management",
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T00:00:00Z",
          messages: [
            {
              id: 1,
              role: "user",
              content: "Show my tasks",
              created_at: "2024-01-01T00:00:00Z",
            },
            {
              id: 2,
              role: "assistant",
              content: "Here are your tasks...",
              created_at: "2024-01-01T00:00:01Z",
            },
          ],
        };

        mockAuthToken("test-token-123");

        mockFetch.mockImplementationOnce(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockConversationDetail),
          })
        );

        const result = await api.getConversation(1);

        expect(result).toEqual(mockConversationDetail);
        expect(result.messages).toHaveLength(2);
        expect(mockFetch).toHaveBeenLastCalledWith(
          "http://localhost:8000/api/conversations/1",
          expect.any(Object)
        );
      });
    });

    describe("deleteConversation", () => {
      it("should send DELETE to conversation endpoint", async () => {
        mockAuthToken("test-token-123");

        mockFetch.mockImplementationOnce(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve({}),
          })
        );

        await api.deleteConversation(1);

        expect(mockFetch).toHaveBeenLastCalledWith(
          "http://localhost:8000/api/conversations/1",
          expect.objectContaining({
            method: "DELETE",
          })
        );
      });
    });
  });

  describe("Authorization header", () => {
    it("should include Bearer token when authenticated", async () => {
      mockAuthToken("my-secure-token");

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        })
      );

      await api.getTasks();

      expect(mockFetch).toHaveBeenLastCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer my-secure-token",
          }),
        })
      );
    });

    it("should not include Authorization header when no token", async () => {
      mockAuthToken(null);

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        })
      );

      await api.getTasks();

      const lastCallHeaders = mockFetch.mock.calls[1][1].headers;
      expect(lastCallHeaders).not.toHaveProperty("Authorization");
    });
  });
});
