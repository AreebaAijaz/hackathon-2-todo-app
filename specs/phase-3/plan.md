# Phase III Implementation Plan

## Architecture
```
ChatKit UI → FastAPI Chat Endpoint → Orchestrator Agent → Subagents → Skills → MCP Tools → Neon DB
```

---

## Phase 1: Database & Models (45 min)
- Create conversations, messages tables
- Update task models if needed
- Add indexes for performance
- Test database operations

## Phase 2: Custom MCP Server (90 min)
- Set up Official MCP SDK
- Implement 5 MCP tools (add, list, complete, delete, update)
- Create tool schemas
- Test tools independently
- Verify database operations

## Phase 3: Skills Library (60 min)
- Build 6 reusable skills
- Task Parser, ID Resolver, Filter Mapper, Confirmation Generator, Error Handler, Context Builder
- Unit test each skill
- Document skill APIs

## Phase 4: Subagents (90 min)
- Build 4 specialized subagents
- CRUD, Query, Completion, Context subagents
- Connect skills to subagents
- Connect MCP tools to subagents
- Test each subagent independently

## Phase 5: Orchestrator Agent (90 min)
- Build main orchestrator with OpenAI Agents SDK
- Implement intent recognition
- Route to appropriate subagents
- Handle multi-turn conversations
- Test orchestration logic

## Phase 6: Chat API Endpoint (60 min)
- Build POST /api/{user_id}/chat
- Implement stateless flow (fetch history, process, save, return)
- Add conversation management
- Test with curl/Postman

## Phase 7: ChatKit Frontend (90 min)
- Install OpenAI ChatKit
- Build chat page component
- Connect to backend API
- Add message history display
- Implement typing indicators
- Style with modern gradients
- Test multi-turn conversations

## Phase 8: Integration & Polish (90 min)
- End-to-end testing (all natural language commands)
- Test multi-agent coordination
- Verify conversation persistence
- Fix bugs
- Polish UI/UX
- Add tool call visualizations
- Performance optimization

## Phase 9: Documentation (30 min)
- Document agent architecture
- Document skills library
- Document MCP tools
- Update README
- Commit to GitHub

---

## Dependencies
```
Phase 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 (sequential)
```

---

## Key Decisions
- **Model:** gpt-4o for orchestrator and subagents
- **MCP SDK:** Official Python MCP SDK
- **Frontend:** Custom Chat UI (modern design matching existing app)
- **State:** Stateless server, all state in Neon DB
- **Auth:** Reuse Better Auth JWT from Phase II

---

## Files to Create

### Backend
```
backend/
├── mcp_server/
│   ├── __init__.py
│   ├── server.py
│   ├── tools.py
│   └── schemas.py
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py
│   └── subagents/
│       ├── __init__.py
│       ├── crud_subagent.py
│       ├── query_subagent.py
│       ├── completion_subagent.py
│       └── context_subagent.py
├── skills/
│   ├── __init__.py
│   ├── task_parser.py
│   ├── id_resolver.py
│   ├── filter_mapper.py
│   ├── confirmation_generator.py
│   ├── error_handler.py
│   └── context_builder.py
├── routes/
│   └── chat.py
└── models.py (update)
```

### Frontend
```
frontend/
├── app/
│   └── chat/
│       └── page.tsx
├── components/
│   └── ChatInterface.tsx
└── lib/
    └── chatApi.ts
```

---

## Dependencies to Add

### Backend (pyproject.toml)
```toml
openai = "^1.0"
mcp = "^1.0"
```

### Frontend (package.json)
- None required (using existing React stack)

---

## Success Metrics
- [ ] All 5 MCP tools working
- [ ] All 6 skills reusable
- [ ] 4 subagents routing correctly
- [ ] Orchestrator handles 20+ natural language variations
- [ ] Conversation persistence works
- [ ] Response time < 3 seconds
- [ ] Mobile responsive UI
