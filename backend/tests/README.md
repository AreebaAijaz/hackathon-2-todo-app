# Backend Test Suite

Comprehensive test suite for the FastAPI Todo application backend.

## Overview

This test suite provides 146 tests covering:
- Pydantic schema validation
- SQLModel model methods
- All AI skill modules (task parsing, filtering, ID resolution, etc.)
- FastAPI route integration tests

## Test Structure

```
tests/
├── __init__.py                          # Package marker
├── conftest.py                          # Shared fixtures (engine, session, client)
├── test_schemas.py                      # Pydantic schema validation tests
├── test_models.py                       # SQLModel model method tests
├── test_skill_task_parser.py            # Task parsing from natural language
├── test_skill_filter_mapper.py          # Filter mapping tests
├── test_skill_id_resolver.py            # Task ID resolution tests
├── test_skill_confirmation_generator.py # Confirmation message tests
├── test_skill_error_handler.py          # Error handling tests
├── test_skill_context_builder.py        # Context building tests
└── test_routes_tasks.py                 # Integration tests for task routes
```

## Running Tests

### Install test dependencies

```bash
cd backend
uv sync --extra test
```

### Run all tests

```bash
uv run pytest tests/
```

### Run specific test file

```bash
uv run pytest tests/test_schemas.py -v
```

### Run with coverage

```bash
uv run pytest tests/ --cov=. --cov-report=html
```

### Run specific test

```bash
uv run pytest tests/test_routes_tasks.py::TestTaskRoutes::test_create_task_with_valid_data -v
```

## Test Coverage

### Schemas (`test_schemas.py`) - 14 tests
- TaskCreate validation (title, description, length constraints)
- TaskUpdate validation (optional fields, constraints)
- TaskResponse from_attributes
- MessageResponse and ErrorResponse creation

### Models (`test_models.py`) - 10 tests
- Message model tool_calls helper methods
- Task model default values
- Conversation model default values

### Skills (90 tests total)

#### TaskParserSkill (`test_skill_task_parser.py`) - 18 tests
- Extract task titles from natural language
- Handle various input formats (prefixes, quotes, separators)
- Extract descriptions from input

#### FilterMapperSkill (`test_skill_filter_mapper.py`) - 20 tests
- Map natural language to filter parameters (all, pending, completed)
- Handle various query phrasings

#### IDResolverSkill (`test_skill_id_resolver.py`) - 18 tests
- Resolve task references by ID (#5, task 5)
- Resolve by ordinal (first, last, second)
- Resolve by title matching

#### ConfirmationGeneratorSkill (`test_skill_confirmation_generator.py`) - 22 tests
- Generate confirmations for CRUD operations
- Handle task listing summaries
- Format change descriptions

#### ErrorHandlerSkill (`test_skill_error_handler.py`) - 12 tests
- Map exceptions to user-friendly messages
- Handle different error types
- Format error responses with suggestions

#### ContextBuilderSkill (`test_skill_context_builder.py`) - 16 tests
- Build conversation context for AI agents
- Extract recent task IDs and last actions
- Truncate history appropriately

### Routes (`test_routes_tasks.py`) - 20 tests
- POST /api/tasks (create)
- GET /api/tasks (list)
- GET /api/tasks/{id} (get)
- PUT /api/tasks/{id} (update)
- DELETE /api/tasks/{id} (delete)
- PATCH /api/tasks/{id}/complete (toggle)
- User isolation
- Health and root endpoints

## Test Fixtures

### `engine`
- Creates an in-memory SQLite database for each test
- Configures `check_same_thread=False` for test compatibility
- Automatically creates and drops tables

### `session`
- Provides a database session within a transaction
- Automatically rolls back after each test

### `client`
- FastAPI TestClient with dependency overrides
- Mocks authentication to return `test-user-id`
- Uses test database session

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    cd backend
    uv sync --extra test
    uv run pytest tests/ -v --tb=short
```

## Notes

- All tests use in-memory SQLite for speed and isolation
- Authentication is mocked using dependency overrides
- Each test gets a fresh database state
- Integration tests use TestClient (no server startup required)
