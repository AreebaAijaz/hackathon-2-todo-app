# Feature Specification: Phase 5A - Advanced Task Features

**Feature Branch**: `001-advanced-task-features`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Add intermediate and advanced level features to existing todo app - priorities, tags, due dates, recurring tasks, search/filter/sort"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prioritize Tasks (Priority: P1)

A user wants to assign priority levels to tasks so they can focus on the most important items first. When creating or editing a task, the user selects a priority (low, medium, high, urgent). The task list displays color-coded priority badges and can be sorted by priority so urgent items appear first.

**Why this priority**: Priority is the most fundamental organizational feature. It immediately adds value to every task and changes how users interact with their entire task list.

**Independent Test**: Can be fully tested by creating tasks with different priorities, verifying badge colors display correctly, and sorting by priority. Delivers immediate organizational value.

**Acceptance Scenarios**:

1. **Given** a user is creating a new task, **When** they do not select a priority, **Then** the task defaults to "medium" priority
2. **Given** a user has tasks with mixed priorities, **When** they sort by priority descending, **Then** urgent tasks appear first, followed by high, medium, low
3. **Given** a task exists with "low" priority, **When** the user edits it to "urgent", **Then** the priority badge updates to red and the change persists
4. **Given** a user views their task list, **When** they look at any task, **Then** they see a color-coded badge (gray=low, yellow=medium, orange=high, red=urgent)

---

### User Story 2 - Tag and Organize Tasks (Priority: P1)

A user wants to label tasks with multiple tags (e.g., "work", "personal", "shopping") to categorize and filter them. When viewing tasks, the user can click a tag to filter the list to only tasks with that tag. Tags appear as clickable pills on each task card.

**Why this priority**: Tags provide the core organizational taxonomy that enables filtering. Combined with priorities, tags transform the app from a flat list into a structured task management system.

**Independent Test**: Can be fully tested by creating tasks with tags, clicking tag pills to filter, and verifying only matching tasks appear. Delivers categorization value.

**Acceptance Scenarios**:

1. **Given** a user is creating a task, **When** they add tags "work" and "urgent", **Then** both tags are saved and displayed as pills on the task card
2. **Given** a user has tasks with various tags, **When** they click the "work" tag pill, **Then** only tasks tagged "work" are displayed
3. **Given** a user tries to add more than 10 tags to a task, **Then** the system prevents it and shows a validation message
4. **Given** a user has never used a tag before, **When** they type a new tag name, **Then** the tag is created and applied
5. **Given** a user has existing tags, **When** they start typing in the tag input, **Then** matching existing tags appear as autocomplete suggestions

---

### User Story 3 - Set Due Dates with Overdue Highlighting (Priority: P1)

A user wants to assign due dates to tasks and see at a glance which tasks are overdue. The task list highlights overdue tasks with a visual warning. Users can filter to see only overdue tasks or tasks due within a date range.

**Why this priority**: Due dates add time awareness to task management. Overdue highlighting creates urgency and prevents tasks from being forgotten. This is essential for any serious task management workflow.

**Independent Test**: Can be fully tested by creating tasks with due dates in the past and future, verifying overdue styling, and filtering by date range.

**Acceptance Scenarios**:

1. **Given** a user creates a task with a due date of tomorrow, **When** they view the task list, **Then** the due date appears in normal styling
2. **Given** a task has a due date that has passed, **When** the user views the task list, **Then** the task shows an overdue visual indicator (red text/icon)
3. **Given** a user wants to find overdue tasks, **When** they toggle the "overdue" filter, **Then** only tasks with past due dates that are not completed are shown
4. **Given** a user creates a task without a due date, **When** they view it, **Then** no due date indicator is shown and the task is not flagged as overdue
5. **Given** a user has tasks with due dates, **When** they sort by due date, **Then** tasks with the earliest due dates appear first and tasks without due dates appear last

---

### User Story 4 - Search Tasks (Priority: P2)

A user wants to quickly find tasks by searching for keywords in the title or description. The search should return relevant results ranked by how well they match the query.

**Why this priority**: Search becomes critical as the number of tasks grows. It enables quick retrieval without manual browsing. Ranked after core organizational features because it supplements rather than replaces browsing.

**Independent Test**: Can be fully tested by creating multiple tasks, searching for keywords, and verifying relevant results appear ranked by relevance.

**Acceptance Scenarios**:

1. **Given** tasks exist with "grocery shopping" and "shop for gifts" titles, **When** the user searches "shop", **Then** both tasks appear in results
2. **Given** a task has "meeting notes" in its description, **When** the user searches "meeting", **Then** the task appears in results
3. **Given** no tasks match the search query, **When** the user searches, **Then** an empty state message "No tasks match your search" is displayed
4. **Given** a user enters a search query, **When** results load, **Then** they appear within 1 second

---

### User Story 5 - Advanced Filtering and Sorting (Priority: P2)

A user wants to combine multiple filters to narrow their task view. They can filter by priority, tags, due date range, overdue status, and completion status simultaneously. They can sort results by created date, due date, priority, or title.

**Why this priority**: Advanced filtering ties together all the new fields into a powerful querying system. It depends on priorities, tags, and due dates being implemented first.

**Independent Test**: Can be fully tested by creating diverse tasks and applying filter combinations, verifying correct results for each combination.

**Acceptance Scenarios**:

1. **Given** a user selects "high" priority filter AND "work" tag filter, **When** results load, **Then** only tasks that are both high priority AND tagged "work" appear
2. **Given** a user sets a date range filter from Feb 1 to Feb 28, **When** results load, **Then** only tasks with due dates within that range appear
3. **Given** active filters are applied, **When** the user clicks "Clear filters", **Then** all filters reset and the full task list is shown
4. **Given** a user changes the sort from "created date" to "priority", **When** the list updates, **Then** tasks reorder by priority level
5. **Given** a user applies filters that match no tasks, **When** results load, **Then** an empty state "No tasks match your filters" is shown with a clear filters option

---

### User Story 6 - Configure Recurring Task Patterns (Priority: P3)

A user wants to mark a task as recurring (daily, weekly, or monthly) to indicate it repeats on a schedule. The recurring pattern is stored and displayed but does not auto-create new task instances in this phase.

**Why this priority**: Recurring tasks add scheduling capability but the actual automation (auto-creating instances) is deferred to Phase 5B. This story only stores the pattern and shows a visual indicator. Lower priority because it's foundational data storage without immediate automation value.

**Independent Test**: Can be fully tested by setting recurring patterns on tasks, verifying the recurring icon displays, and confirming the pattern persists through edits.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** they set recurrence to "weekly", **Then** the task shows a recurring indicator icon and the pattern is saved
2. **Given** a recurring task exists, **When** the user completes it, **Then** the current instance is marked complete (no new instance is auto-created in this phase)
3. **Given** a user edits a task's recurrence, **When** they change from "daily" to "monthly", **Then** the pattern updates and the display reflects the change
4. **Given** a user creates a task without setting recurrence, **When** they view it, **Then** no recurring indicator is shown and the pattern defaults to "none"

---

### User Story 7 - Chatbot Understands Advanced Features (Priority: P2)

A user wants to manage tasks with the new features via the AI chatbot. They can say things like "add a high priority task to buy groceries due Friday tagged shopping" and the chatbot correctly creates the task with all specified attributes. They can also filter via natural language: "show my overdue work tasks".

**Why this priority**: The chatbot is a key interface in this app. Supporting new features through natural language maintains feature parity between UI and chat. Ranked P2 because it depends on the backend supporting these features first.

**Independent Test**: Can be fully tested by issuing natural language commands and verifying the chatbot correctly parses and applies priority, tags, due dates, and filters.

**Acceptance Scenarios**:

1. **Given** a user tells the chatbot "add a high priority task to call dentist due next Monday tagged health", **When** the task is created, **Then** it has priority=high, due_date=next Monday, tags=["health"]
2. **Given** a user asks "show my urgent tasks", **When** results load, **Then** only tasks with priority=urgent are listed
3. **Given** a user asks "what tasks are overdue?", **When** results load, **Then** only tasks past their due date and not completed are shown
4. **Given** a user says "tag the groceries task as personal", **When** the update completes, **Then** the "personal" tag is added to the matching task

---

### Edge Cases

- What happens when a user sets a due date in the past? The task is created but immediately flagged as overdue.
- What happens when a user searches with an empty query? All tasks are returned (no filter applied).
- What happens when a user applies conflicting filters (e.g., priority=low AND overdue toggle) that match no tasks? An empty state is shown with option to clear filters.
- What happens when a tag contains special characters? Tags are trimmed of whitespace and limited to alphanumeric characters, hyphens, and underscores. Max 30 characters per tag.
- What happens when a user sorts by due date but some tasks have no due date? Tasks without due dates appear at the end of the sorted list.
- What happens when the database migration runs on existing tasks? Existing tasks receive default values: priority="medium", tags=[], due_date=null, recurring_pattern="none", recurring_enabled=false.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support four priority levels for tasks: low, medium, high, urgent. Default priority is "medium".
- **FR-002**: System MUST display color-coded priority badges on task cards (gray=low, yellow=medium, orange=high, red=urgent).
- **FR-003**: System MUST allow users to assign up to 10 tags per task, each tag max 30 characters, alphanumeric with hyphens and underscores.
- **FR-004**: System MUST display tags as clickable pills on task cards that trigger filtering when clicked.
- **FR-005**: System MUST provide tag autocomplete suggestions from the user's existing tags when entering tags.
- **FR-006**: System MUST support optional due dates on tasks with timezone-aware datetime storage.
- **FR-007**: System MUST visually highlight overdue tasks (past due date, not completed) with a distinct warning style.
- **FR-008**: System MUST support full-text search across task titles and descriptions with relevance-ranked results.
- **FR-009**: System MUST support filtering tasks by: completion status, priority level(s), tag(s), due date range, and overdue status. Filters combine with AND logic.
- **FR-010**: System MUST support sorting tasks by: created date, due date, priority, and title. Both ascending and descending order.
- **FR-011**: System MUST handle null due dates in sorting by placing them at the end of results regardless of sort direction.
- **FR-012**: System MUST support recurring task patterns (daily, weekly, monthly, none) stored on the task. Default is "none".
- **FR-013**: System MUST display a recurring indicator icon on tasks with a non-"none" recurring pattern.
- **FR-014**: System MUST NOT auto-create new recurring task instances in this phase (deferred to Phase 5B).
- **FR-015**: System MUST provide a dedicated endpoint to retrieve all unique tags used by a user for autocomplete.
- **FR-016**: System MUST support bulk operations: update priority, add tags, and set due dates for multiple tasks at once.
- **FR-017**: System MUST run a database migration that adds new fields to existing tasks with safe defaults and no data loss.
- **FR-018**: System MUST update the AI chatbot to parse and apply priority, tags, due dates, and recurring patterns from natural language input.
- **FR-019**: System MUST update the AI chatbot to support natural language filtering ("show overdue tasks", "find urgent work tasks").
- **FR-020**: System MUST show appropriate empty states when filters/search return no results, with an option to clear filters.

### Key Entities

- **Task** (updated): Core entity representing a user's to-do item. Existing fields: id, user_id, title, description, completed, created_at, updated_at. New fields: priority (enum string), tags (list of strings), due_date (optional datetime), recurring_pattern (optional string), recurring_enabled (boolean).
- **Tag**: A user-defined label string associated with tasks. Not a standalone entity — stored as a list directly on the Task. Queryable across all user's tasks for autocomplete and filtering.

## Scope *(mandatory)*

### In Scope

- Priority system (CRUD, display, sort, filter)
- Tag system (CRUD, autocomplete, filter, clickable pills)
- Due dates (CRUD, overdue detection, date range filtering, sort)
- Recurring task pattern storage and display (no auto-creation)
- Full-text search on title and description
- Advanced multi-field filtering with AND logic
- Multi-field sorting with null handling
- Chatbot natural language support for all new features
- Database migration for existing tasks
- Updated MCP tools for agent/chatbot integration
- Both Vercel and Kubernetes deployment compatibility

### Out of Scope

- Kafka event streaming (Phase 5B)
- Dapr sidecar integration (Phase 5B)
- Notification/reminder service (Phase 5B)
- Automatic recurring task instance creation (Phase 5B)
- Cloud deployment to DigitalOcean DOKS (Phase 5C)
- Shared/collaborative tags across users
- Task dependencies or subtasks
- File attachments on tasks
- Pagination (acceptable to defer since task volume per user is expected to be <500)

## Assumptions

- Users have fewer than 500 tasks each, so pagination is not critical for this phase.
- The existing Neon PostgreSQL database supports array types and full-text search (tsvector).
- The existing Better Auth session system continues to handle authentication; no auth changes needed.
- Tag autocomplete is scoped to the current user's tags only, not global.
- Due dates are stored in UTC and displayed in the user's local timezone (browser handles conversion).
- The recurring pattern field is informational in this phase; no cron jobs or scheduled task creation.
- Bulk operations are limited to same-user tasks and require authentication.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with priority, tags, due date, and recurring pattern in under 30 seconds from the creation form.
- **SC-002**: Task list correctly filters by any combination of priority, tags, due date range, and overdue status, returning accurate results within 1 second.
- **SC-003**: Full-text search returns relevant tasks ranked by relevance within 1 second for queries up to 200 characters.
- **SC-004**: Overdue tasks are visually distinguishable from on-time tasks without any user action (automatic highlighting).
- **SC-005**: Users can sort task list by any supported field (created date, due date, priority, title) in both ascending and descending order.
- **SC-006**: The AI chatbot correctly parses priority, tags, and due dates from natural language commands with at least 90% accuracy for standard phrasing.
- **SC-007**: Database migration completes on existing data with zero data loss and all existing tasks receive valid defaults.
- **SC-008**: All new features function identically on both Vercel and Kubernetes deployments.
- **SC-009**: Tag autocomplete suggestions appear within 500ms of the user starting to type.
- **SC-010**: All filter, sort, and search operations complete within 500ms for a dataset of 500 tasks.

## Dependencies

- Phase II/III working app (existing Vercel + Kubernetes deployments)
- Neon PostgreSQL with array type and full-text search support
- Better Auth session management (existing)
- OpenAI API for chatbot natural language understanding (existing)
- MCP tool framework for agent integration (existing)
