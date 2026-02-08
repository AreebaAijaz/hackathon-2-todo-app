# Data Model: Advanced Task Features

**Feature Branch**: `001-advanced-task-features`
**Created**: 2026-02-08
**Research**: [research.md](./research.md)

## Entity: Task (Updated)

### Current Schema (Phase II/III)

```sql
CREATE TABLE tasks (
    id          SERIAL PRIMARY KEY,
    user_id     VARCHAR NOT NULL,        -- References Better Auth "user" table
    title       VARCHAR(200) NOT NULL,
    description VARCHAR(500) DEFAULT '',
    completed   BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_tasks_user_id ON tasks (user_id);
CREATE INDEX ix_tasks_completed ON tasks (completed);
```

### New Schema (Phase 5A)

```sql
CREATE TABLE tasks (
    -- Existing columns (unchanged)
    id               SERIAL PRIMARY KEY,
    user_id          VARCHAR NOT NULL,
    title            VARCHAR(200) NOT NULL,
    description      VARCHAR(500) DEFAULT '',
    completed        BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW(),

    -- New columns (Phase 5A)
    priority         VARCHAR(10) DEFAULT 'medium'
                     CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    tags             TEXT[] DEFAULT '{}',
    due_date         TIMESTAMPTZ DEFAULT NULL,
    recurring_pattern VARCHAR(10) DEFAULT 'none'
                     CHECK (recurring_pattern IN ('none', 'daily', 'weekly', 'monthly')),
    search_vector    TSVECTOR
);

-- Existing indexes
CREATE INDEX ix_tasks_user_id ON tasks (user_id);
CREATE INDEX ix_tasks_completed ON tasks (completed);

-- New indexes (Phase 5A)
CREATE INDEX ix_tasks_priority ON tasks (priority);
CREATE INDEX ix_tasks_due_date ON tasks (due_date);
CREATE INDEX ix_tasks_tags ON tasks USING GIN (tags);
CREATE INDEX ix_tasks_search ON tasks USING GIN (search_vector);
```

### Search Vector Trigger

```sql
-- Auto-update search_vector on INSERT or UPDATE of title/description
CREATE OR REPLACE FUNCTION tasks_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', NEW.title || ' ' || COALESCE(NEW.description, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_search_vector_trigger
    BEFORE INSERT OR UPDATE OF title, description
    ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION tasks_search_vector_update();
```

## SQLModel Definition (Python)

```python
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Text, ARRAY, text
from sqlalchemy.dialects.postgresql import TSVECTOR

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Existing fields
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=500)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # New fields (Phase 5A)
    priority: str = Field(default="medium", index=True)
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Text), server_default=text("'{}'::text[]"))
    )
    due_date: Optional[datetime] = Field(default=None, index=True)
    recurring_pattern: str = Field(default="none")
    search_vector: Optional[str] = Field(
        default=None,
        sa_column=Column(TSVECTOR)
    )
```

## Pydantic Schemas (API Layer)

### TaskCreate (updated)

```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    tags: List[str] = Field(default_factory=list, max_length=10)
    due_date: Optional[datetime] = None
    recurring_pattern: str = Field(default="none", pattern="^(none|daily|weekly|monthly)$")
```

### TaskUpdate (updated)

```python
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high|urgent)$")
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    recurring_pattern: Optional[str] = Field(default=None, pattern="^(none|daily|weekly|monthly)$")
```

### TaskResponse (updated)

```python
class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    recurring_pattern: str
    is_overdue: bool  # Computed field

    class Config:
        from_attributes = True
```

### BulkUpdateRequest (new)

```python
class BulkUpdateRequest(BaseModel):
    task_ids: List[int] = Field(..., min_length=1, max_length=50)
    operations: BulkOperations

class BulkOperations(BaseModel):
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high|urgent)$")
    add_tags: Optional[List[str]] = None
    remove_tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    recurring_pattern: Optional[str] = Field(default=None, pattern="^(none|daily|weekly|monthly)$")

class BulkUpdateResponse(BaseModel):
    updated_count: int
    task_ids: List[int]
```

### TaskFilterParams (new)

```python
class TaskFilterParams(BaseModel):
    status: Optional[str] = Field(default=None, pattern="^(all|pending|completed)$")
    priority: Optional[List[str]] = None  # comma-separated in URL
    tags: Optional[List[str]] = None      # comma-separated in URL
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    overdue: Optional[bool] = None
    search: Optional[str] = Field(default=None, max_length=200)
    sort_by: str = Field(default="created_at", pattern="^(created_at|due_date|priority|title)$")
    sort_dir: str = Field(default="desc", pattern="^(asc|desc)$")
```

## Migration Script (Alembic)

### Forward Migration

```python
def upgrade():
    # Add new columns with defaults
    op.add_column('tasks', sa.Column('priority', sa.String(10),
                  server_default='medium', nullable=False))
    op.add_column('tasks', sa.Column('tags', ARRAY(sa.Text),
                  server_default=text("'{}'::text[]"), nullable=False))
    op.add_column('tasks', sa.Column('due_date',
                  sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('recurring_pattern', sa.String(10),
                  server_default='none', nullable=False))
    op.add_column('tasks', sa.Column('search_vector', TSVECTOR, nullable=True))

    # Add CHECK constraints
    op.create_check_constraint('ck_tasks_priority', 'tasks',
        "priority IN ('low', 'medium', 'high', 'urgent')")
    op.create_check_constraint('ck_tasks_recurring', 'tasks',
        "recurring_pattern IN ('none', 'daily', 'weekly', 'monthly')")

    # Add indexes
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('ix_tasks_tags', 'tasks', ['tags'], postgresql_using='gin')
    op.create_index('ix_tasks_search', 'tasks', ['search_vector'], postgresql_using='gin')

    # Create search vector trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION tasks_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', NEW.title || ' ' || COALESCE(NEW.description, ''));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER tasks_search_vector_trigger
            BEFORE INSERT OR UPDATE OF title, description
            ON tasks FOR EACH ROW
            EXECUTE FUNCTION tasks_search_vector_update();
    """)

    # Backfill search_vector for existing rows
    op.execute("""
        UPDATE tasks SET search_vector = to_tsvector('english', title || ' ' || COALESCE(description, ''));
    """)
```

### Reverse Migration

```python
def downgrade():
    op.execute("DROP TRIGGER IF EXISTS tasks_search_vector_trigger ON tasks")
    op.execute("DROP FUNCTION IF EXISTS tasks_search_vector_update()")
    op.drop_index('ix_tasks_search', 'tasks')
    op.drop_index('ix_tasks_tags', 'tasks')
    op.drop_index('ix_tasks_due_date', 'tasks')
    op.drop_index('ix_tasks_priority', 'tasks')
    op.drop_constraint('ck_tasks_recurring', 'tasks')
    op.drop_constraint('ck_tasks_priority', 'tasks')
    op.drop_column('tasks', 'search_vector')
    op.drop_column('tasks', 'recurring_pattern')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
```

## TypeScript Interface (Frontend)

```typescript
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  // Phase 5A fields
  priority: "low" | "medium" | "high" | "urgent";
  tags: string[];
  due_date: string | null;
  recurring_pattern: "none" | "daily" | "weekly" | "monthly";
  is_overdue: boolean;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  priority?: "low" | "medium" | "high" | "urgent";
  tags?: string[];
  due_date?: string;
  recurring_pattern?: "none" | "daily" | "weekly" | "monthly";
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  priority?: "low" | "medium" | "high" | "urgent";
  tags?: string[];
  due_date?: string | null;
  recurring_pattern?: "none" | "daily" | "weekly" | "monthly";
}

export interface TaskFilters {
  status?: "all" | "pending" | "completed";
  priority?: string[];
  tags?: string[];
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
    priority?: "low" | "medium" | "high" | "urgent";
    add_tags?: string[];
    remove_tags?: string[];
    due_date?: string;
    recurring_pattern?: "none" | "daily" | "weekly" | "monthly";
  };
}
```

## Validation Rules

| Field | Rule | Enforced At |
|-------|------|-------------|
| priority | Must be `low\|medium\|high\|urgent` | DB CHECK + Pydantic |
| tags | Max 10 items | Pydantic validator |
| tags (each) | Max 30 chars, `^[a-zA-Z0-9_-]+$` | Pydantic validator |
| due_date | Valid ISO 8601 or null | Pydantic |
| recurring_pattern | Must be `none\|daily\|weekly\|monthly` | DB CHECK + Pydantic |
| search query | Max 200 chars | Pydantic |
| bulk task_ids | 1-50 IDs | Pydantic validator |
