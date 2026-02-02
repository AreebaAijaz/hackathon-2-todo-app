import {
  Task,
  CreateTaskInput,
  UpdateTaskInput,
  User,
  ApiError,
  ChatMessage,
  Conversation,
  ConversationDetail,
  ChatRequest,
  ChatResponse,
} from "../lib/types";

describe("TypeScript Type Definitions", () => {
  describe("Task interface", () => {
    it("should create a valid Task object with all required fields", () => {
      const task: Task = {
        id: 1,
        user_id: "user-123",
        title: "Test Task",
        description: "Test Description",
        completed: false,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      expect(task.id).toBe(1);
      expect(task.user_id).toBe("user-123");
      expect(task.title).toBe("Test Task");
      expect(task.description).toBe("Test Description");
      expect(task.completed).toBe(false);
      expect(task.created_at).toBe("2024-01-01T00:00:00Z");
      expect(task.updated_at).toBe("2024-01-01T00:00:00Z");
    });
  });

  describe("CreateTaskInput interface", () => {
    it("should create a CreateTaskInput with just title", () => {
      const input: CreateTaskInput = {
        title: "New Task",
      };

      expect(input.title).toBe("New Task");
      expect(input.description).toBeUndefined();
    });

    it("should create a CreateTaskInput with title and description", () => {
      const input: CreateTaskInput = {
        title: "New Task",
        description: "Task description",
      };

      expect(input.title).toBe("New Task");
      expect(input.description).toBe("Task description");
    });
  });

  describe("UpdateTaskInput interface", () => {
    it("should create an UpdateTaskInput with all fields optional", () => {
      const input1: UpdateTaskInput = {};
      expect(input1.title).toBeUndefined();
      expect(input1.description).toBeUndefined();

      const input2: UpdateTaskInput = {
        title: "Updated Title",
      };
      expect(input2.title).toBe("Updated Title");
      expect(input2.description).toBeUndefined();

      const input3: UpdateTaskInput = {
        description: "Updated Description",
      };
      expect(input3.title).toBeUndefined();
      expect(input3.description).toBe("Updated Description");

      const input4: UpdateTaskInput = {
        title: "Updated Title",
        description: "Updated Description",
      };
      expect(input4.title).toBe("Updated Title");
      expect(input4.description).toBe("Updated Description");
    });
  });

  describe("User interface", () => {
    it("should create a valid User object", () => {
      const user: User = {
        id: "user-123",
        email: "test@example.com",
        name: "Test User",
      };

      expect(user.id).toBe("user-123");
      expect(user.email).toBe("test@example.com");
      expect(user.name).toBe("Test User");
    });
  });

  describe("ApiError interface", () => {
    it("should create a valid ApiError object", () => {
      const error: ApiError = {
        detail: "Something went wrong",
      };

      expect(error.detail).toBe("Something went wrong");
    });
  });

  describe("ChatMessage interface", () => {
    it("should create a ChatMessage with role 'user'", () => {
      const message: ChatMessage = {
        id: 1,
        role: "user",
        content: "Hello, assistant!",
        created_at: "2024-01-01T00:00:00Z",
      };

      expect(message.id).toBe(1);
      expect(message.role).toBe("user");
      expect(message.content).toBe("Hello, assistant!");
      expect(message.created_at).toBe("2024-01-01T00:00:00Z");
    });

    it("should create a ChatMessage with role 'assistant'", () => {
      const message: ChatMessage = {
        id: 2,
        role: "assistant",
        content: "Hello! How can I help you?",
        tool_calls: [{ name: "get_tasks", args: {} }],
        created_at: "2024-01-01T00:00:01Z",
      };

      expect(message.id).toBe(2);
      expect(message.role).toBe("assistant");
      expect(message.content).toBe("Hello! How can I help you?");
      expect(message.tool_calls).toHaveLength(1);
      expect(message.created_at).toBe("2024-01-01T00:00:01Z");
    });

    it("should create a ChatMessage with role 'system'", () => {
      const message: ChatMessage = {
        role: "system",
        content: "You are a helpful assistant.",
      };

      expect(message.role).toBe("system");
      expect(message.content).toBe("You are a helpful assistant.");
      expect(message.id).toBeUndefined();
    });
  });

  describe("ChatRequest interface", () => {
    it("should create a ChatRequest with just message", () => {
      const request: ChatRequest = {
        message: "What are my tasks?",
      };

      expect(request.message).toBe("What are my tasks?");
      expect(request.conversation_id).toBeUndefined();
    });

    it("should create a ChatRequest with message and conversation_id", () => {
      const request: ChatRequest = {
        message: "Add a new task",
        conversation_id: 42,
      };

      expect(request.message).toBe("Add a new task");
      expect(request.conversation_id).toBe(42);
    });
  });

  describe("ChatResponse interface", () => {
    it("should verify ChatResponse shape", () => {
      const response: ChatResponse = {
        reply: "I've added the task for you.",
        conversation_id: 42,
        tool_calls: [{ name: "create_task", result: "success" }],
      };

      expect(response.reply).toBe("I've added the task for you.");
      expect(response.conversation_id).toBe(42);
      expect(response.tool_calls).toHaveLength(1);
    });
  });

  describe("Conversation interface", () => {
    it("should verify Conversation shape", () => {
      const conversation: Conversation = {
        id: 1,
        user_id: "user-123",
        title: "Task Management Chat",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      expect(conversation.id).toBe(1);
      expect(conversation.user_id).toBe("user-123");
      expect(conversation.title).toBe("Task Management Chat");
      expect(conversation.created_at).toBe("2024-01-01T00:00:00Z");
      expect(conversation.updated_at).toBe("2024-01-01T00:00:00Z");
    });

    it("should allow null title in Conversation", () => {
      const conversation: Conversation = {
        id: 1,
        user_id: "user-123",
        title: null,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      expect(conversation.title).toBeNull();
    });
  });

  describe("ConversationDetail interface", () => {
    it("should verify ConversationDetail with messages array", () => {
      const messages: ChatMessage[] = [
        {
          id: 1,
          role: "user",
          content: "Hello",
          created_at: "2024-01-01T00:00:00Z",
        },
        {
          id: 2,
          role: "assistant",
          content: "Hi there!",
          created_at: "2024-01-01T00:00:01Z",
        },
      ];

      const conversationDetail: ConversationDetail = {
        id: 1,
        user_id: "user-123",
        title: "Test Chat",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:01Z",
        messages: messages,
      };

      expect(conversationDetail.id).toBe(1);
      expect(conversationDetail.user_id).toBe("user-123");
      expect(conversationDetail.title).toBe("Test Chat");
      expect(conversationDetail.messages).toHaveLength(2);
      expect(conversationDetail.messages[0].role).toBe("user");
      expect(conversationDetail.messages[1].role).toBe("assistant");
    });

    it("should allow empty messages array", () => {
      const conversationDetail: ConversationDetail = {
        id: 1,
        user_id: "user-123",
        title: null,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
        messages: [],
      };

      expect(conversationDetail.messages).toHaveLength(0);
    });
  });
});
