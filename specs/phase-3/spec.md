# Phase III - AI Chatbot with Multi-Agent Architecture & MCP Tools

## Goal
Build conversational AI chatbot using OpenAI Agents SDK, custom MCP server, multi-agent orchestration with subagents and reusable skills for maximum sophistication.

---

## Multi-Agent Architecture

### Main Agent: Todo Orchestrator Agent
- **Role:** Receives natural language, understands intent, routes to specialized subagents
- **Tech:** OpenAI Agents SDK with gpt-4o model
- **Responsibilities:** Command parsing, subagent coordination, response synthesis
- **Context:** Loads conversation history from database for continuity

### Subagent 1: Task CRUD Subagent
- **Role:** Create, update, delete tasks
- **MCP Tools:** add_task, update_task, delete_task
- **Skills:** Task Parser, Input Validator, Confirmation Generator
- **Example:** "Add buy groceries" → Uses Task Parser skill → Calls add_task MCP tool

### Subagent 2: Task Query Subagent
- **Role:** Search, filter, list tasks
- **MCP Tools:** list_tasks
- **Skills:** Status Filter Mapper, Result Formatter, Empty State Handler
- **Example:** "Show pending tasks" → Uses Filter Mapper skill → Calls list_tasks with filter

### Subagent 3: Task Completion Subagent
- **Role:** Mark tasks complete/incomplete
- **MCP Tools:** complete_task
- **Skills:** Task ID Resolver, Status Toggler, Success Confirmer
- **Example:** "Mark meeting done" → Uses ID Resolver skill → Calls complete_task

### Subagent 4: Context Management Subagent
- **Role:** Maintain conversation context, handle follow-ups
- **Database:** Fetch message history
- **Skills:** Context Builder, Intent Tracker, Ambiguity Resolver
- **Example:** "What did I add?" → Loads conversation history → Summarizes recent adds

---

## Reusable Skills Library (6 Skills)

### Skill 1: Natural Language Task Parser
- **Input:** "Buy groceries and milk tomorrow"
- **Output:** `{title: "Buy groceries and milk", description: "", metadata: {date_mention: "tomorrow"}}`
- **Used by:** Task CRUD Subagent

### Skill 2: Task ID Resolver
- **Input:** "meeting task" or "task 3" or "the first one"
- **Output:** Resolved task_id from database
- **Used by:** Task Completion, Task CRUD (for updates/deletes)

### Skill 3: Status Filter Mapper
- **Input:** "pending", "done", "everything", "incomplete"
- **Output:** DB filter value ("pending", "completed", "all")
- **Used by:** Task Query Subagent

### Skill 4: Confirmation Message Generator
- **Input:** Action + result (e.g., "created", task object)
- **Output:** Friendly confirmation ("✅ Added 'Buy groceries' to your list!")
- **Used by:** All subagents

### Skill 5: Error Handler
- **Input:** Exception/error type
- **Output:** User-friendly error message
- **Used by:** All subagents

### Skill 6: Conversation Context Builder
- **Input:** Database messages
- **Output:** Formatted message array for OpenAI Agents
- **Used by:** Context Management Subagent

---

## Custom MCP Server (Official MCP SDK)

- **Location:** backend/mcp_server/
- **Purpose:** Expose task operations as standardized MCP tools
- **Tech:** Official MCP SDK (Python)

### MCP Tool 1: add_task
- **Parameters:** user_id (string), title (string), description (string, optional)
- **Returns:** `{task_id, status: "created", title}`
- **Database:** INSERT INTO tasks

### MCP Tool 2: list_tasks
- **Parameters:** user_id (string), status (string: "all"/"pending"/"completed")
- **Returns:** Array of `{id, title, description, completed, created_at}`
- **Database:** SELECT FROM tasks WHERE user_id AND status filter

### MCP Tool 3: complete_task
- **Parameters:** user_id (string), task_id (integer)
- **Returns:** `{task_id, status: "completed", title}`
- **Database:** UPDATE tasks SET completed=true

### MCP Tool 4: delete_task
- **Parameters:** user_id (string), task_id (integer)
- **Returns:** `{task_id, status: "deleted", title}`
- **Database:** DELETE FROM tasks

### MCP Tool 5: update_task
- **Parameters:** user_id (string), task_id (integer), title (optional), description (optional)
- **Returns:** `{task_id, status: "updated", title}`
- **Database:** UPDATE tasks SET ...

---

## Stateless Chat Architecture

### API Endpoint
`POST /api/{user_id}/chat`

**Request:**
```json
{
  "conversation_id": "optional",
  "message": "string"
}
```

**Response:**
```json
{
  "conversation_id": "string",
  "response": "string",
  "tool_calls": []
}
```

### Flow (Stateless)
1. Receive user message
2. Fetch conversation history from DB (messages table)
3. Build context array (previous messages + new message)
4. Store user message in DB
5. Pass to Todo Orchestrator Agent
6. Orchestrator routes to appropriate subagent(s)
7. Subagent uses skills + MCP tools
8. Store assistant response in DB
9. Return response to client
10. Server forgets everything (ready for next request)

---

## Database Schema

### conversations table
```sql
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### messages table
```sql
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  conversation_id INTEGER REFERENCES conversations(id),
  user_id VARCHAR NOT NULL,
  role VARCHAR NOT NULL, -- user/assistant/system
  content TEXT NOT NULL,
  tool_calls JSON, -- optional, log which MCP tools were called
  created_at TIMESTAMP DEFAULT NOW()
);
```

### tasks table (already exists from Phase II)
- id, user_id, title, description, completed, created_at, updated_at

---

## Frontend (Chat UI)

- **Location:** frontend/app/chat/
- **Features:**
  - Message history display
  - Input field with send button
  - Typing indicators
  - Tool call badges (show which MCP tools were invoked)
  - Conversation persistence (resume after refresh)
  - Mobile responsive
  - Beautiful modern design with gradients

---

## Natural Language Examples

| User Input | Flow | Response |
|------------|------|----------|
| "Add buy groceries" | Orchestrator → CRUD Subagent → Task Parser → add_task | "✅ Added 'Buy groceries' to your list!" |
| "Show pending tasks" | Orchestrator → Query Subagent → Filter Mapper → list_tasks | "You have 3 pending tasks: 1. Buy groceries..." |
| "Mark the meeting task as done" | Orchestrator → Completion Subagent → ID Resolver → complete_task | "✅ Marked 'Team meeting' as complete!" |
| "What did I add today?" | Orchestrator → Context Subagent → Context Builder → Query messages | "Today you added: Buy groceries, Call mom..." |
| "Delete task 2" | Orchestrator → CRUD Subagent → delete_task | "🗑️ Deleted 'Call mom' from your list" |

---

## Tech Stack

- **Frontend:** Next.js 15, TypeScript, Tailwind CSS
- **Backend:** FastAPI, OpenAI Agents SDK, Official MCP SDK
- **Database:** Neon Postgres (conversations, messages, tasks)
- **Auth:** Better Auth with JWT (from Phase II)

---

## Success Criteria

- [ ] Orchestrator agent routes to correct subagent 100% of time
- [ ] All 6 skills reusable across subagents
- [ ] All 5 MCP tools functional
- [ ] Chatbot understands 20+ natural language variations
- [ ] Conversation persists across sessions
- [ ] Stateless server (no in-memory state)
- [ ] Multi-turn context works
- [ ] Tool calls logged in database
- [ ] Beautiful Chat UI with modern design
- [ ] Mobile responsive
- [ ] Response time <3 seconds
- [ ] Graceful error handling

---

## Not Building

- Voice input (text only)
- File attachments
- Image generation
- Admin dashboard
- Analytics UI
