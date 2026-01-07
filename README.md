# Evolution of Todo

A 5-phase hackathon project demonstrating the evolution of a Todo application from console app to cloud-native Kubernetes deployment.

## Current Phase: I - Console Application

In-memory Python CLI todo app with Rich formatting.

## Quick Start

```bash
# Prerequisites: Python 3.13+, UV package manager

# Install dependencies
uv sync

# Run the application
uv run python -m src.main

# Run tests
uv run pytest -v

# Check coverage
uv run pytest --cov=src --cov-report=term-missing
```

## Features

| Feature | Description |
|---------|-------------|
| Add Task | Create task with title and optional description |
| View All | Display tasks in formatted table |
| Update Task | Modify title/description by ID |
| Delete Task | Remove task with confirmation |
| Mark Complete | Toggle completion status |

## Project Structure

```
hackathon-2/
├── src/
│   ├── __init__.py
│   ├── main.py          # Entry point
│   ├── models.py        # Task dataclass
│   ├── storage.py       # In-memory CRUD
│   └── cli.py           # Rich CLI interface
├── tests/
│   ├── test_models.py   # Model tests
│   └── test_storage.py  # Storage tests
├── specs/
│   ├── constitution.md  # Project standards
│   └── phase-1/         # Phase I specs
├── pyproject.toml       # UV config
├── CLAUDE.md            # AI instructions
└── README.md
```

## Usage Example

```
===== Todo App Menu =====
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Complete/Incomplete
6. Exit

Enter choice: 1
Enter task title: Buy groceries
Enter description (optional): Milk, eggs, bread
Task created successfully! ID: a1b2c3d4...
```

## Phase Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| I | Console Application | **Complete** |
| II | Full-Stack Web App | Pending |
| III | AI Chatbot Integration | Pending |
| IV | Kubernetes Deployment | Pending |
| V | Production Cloud | Pending |

## Development Standards

All development follows the [Project Constitution](specs/constitution.md).

- Type hints on all Python code
- Docstrings on all functions
- 80%+ test coverage on business logic
- Rich library for CLI formatting
