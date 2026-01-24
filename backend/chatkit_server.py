"""ChatKit Protocol Implementation for Task Management Bot.

Implements the OpenAI ChatKit protocol using our multi-agent orchestrator.
This allows the frontend ChatKit component to communicate with our backend.
"""

import os
import json
import uuid
from typing import AsyncGenerator, Dict, Any, Optional
from dataclasses import dataclass

from openai import OpenAI

from mcp_server import (
    add_task, AddTaskInput,
    list_tasks, ListTasksInput,
    complete_task, CompleteTaskInput,
    delete_task, DeleteTaskInput,
    update_task, UpdateTaskInput,
    TaskNotFoundError, UnauthorizedError,
)


# ============== ChatKit Protocol Types ==============

@dataclass
class ChatKitMessage:
    """Represents a message in ChatKit format."""
    id: str
    role: str
    content: str
    content_type: str = "output_text"


# ============== Tool Definitions for OpenAI ==============

CHATKIT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the user's task list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the task"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List tasks with optional filtering by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by task status"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "Task ID or title to identify the task"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task from the list",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "Task ID or title to identify the task"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "Task ID or title to identify the task"
                    },
                    "new_title": {
                        "type": "string",
                        "description": "New title for the task"
                    },
                    "new_description": {
                        "type": "string",
                        "description": "New description for the task"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a helpful AI assistant for task management.
You help users create, view, complete, and manage their tasks.

When users ask about tasks, use the available tools:
- add_task: Create new tasks
- list_tasks: Show tasks (filter by all/pending/completed)
- complete_task: Mark tasks as done
- delete_task: Remove tasks
- update_task: Modify task title or description

Be conversational and friendly. Confirm actions clearly.
If a user's request is ambiguous, ask for clarification.
Format task lists nicely for readability."""


class ChatKitServer:
    """Implements ChatKit protocol for streaming responses."""

    def __init__(self):
        """Initialize the ChatKit server."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any], user_id: str) -> str:
        """Execute a tool call and return the result as a string."""
        try:
            if tool_name == "add_task":
                result = add_task(AddTaskInput(
                    user_id=user_id,
                    title=arguments.get("title", ""),
                    description=arguments.get("description", "")
                ))
                return f"Created task: {result.title}"

            elif tool_name == "list_tasks":
                result = list_tasks(ListTasksInput(
                    user_id=user_id,
                    status=arguments.get("status", "all")
                ))
                if not result.tasks:
                    filter_msg = f" ({result.filter_applied})" if result.filter_applied != "all" else ""
                    return f"No tasks found{filter_msg}."

                lines = [f"Found {result.count} task(s):"]
                for t in result.tasks:
                    status_icon = "[x]" if t.completed else "[ ]"
                    line = f"{status_icon} {t.title}"
                    if t.description:
                        line += f" - {t.description}"
                    lines.append(line)
                return "\n".join(lines)

            elif tool_name == "complete_task":
                task_id = self._resolve_task_id(arguments.get("task_identifier", ""), user_id)
                if task_id is None:
                    return f"Could not find task matching: {arguments.get('task_identifier', '')}"

                result = complete_task(CompleteTaskInput(
                    user_id=user_id,
                    task_id=task_id
                ))
                if result.status == "already_completed":
                    return f"Task '{result.title}' was already completed."
                return f"Completed task: {result.title}"

            elif tool_name == "delete_task":
                task_id = self._resolve_task_id(arguments.get("task_identifier", ""), user_id)
                if task_id is None:
                    return f"Could not find task matching: {arguments.get('task_identifier', '')}"

                result = delete_task(DeleteTaskInput(
                    user_id=user_id,
                    task_id=task_id
                ))
                return f"Deleted task: {result.title}"

            elif tool_name == "update_task":
                task_id = self._resolve_task_id(arguments.get("task_identifier", ""), user_id)
                if task_id is None:
                    return f"Could not find task matching: {arguments.get('task_identifier', '')}"

                result = update_task(UpdateTaskInput(
                    user_id=user_id,
                    task_id=task_id,
                    title=arguments.get("new_title"),
                    description=arguments.get("new_description")
                ))
                changes = ", ".join(result.changes) if result.changes else "no changes"
                return f"Updated task '{result.title}': {changes}"

            else:
                return f"Unknown tool: {tool_name}"

        except TaskNotFoundError as e:
            return str(e)
        except UnauthorizedError as e:
            return str(e)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def _resolve_task_id(self, identifier: str, user_id: str) -> Optional[int]:
        """Resolve a task identifier to a task ID."""
        # Try to parse as integer first
        try:
            return int(identifier)
        except ValueError:
            pass

        # Search by title
        result = list_tasks(ListTasksInput(user_id=user_id, status="all"))
        for t in result.tasks:
            if identifier.lower() in t.title.lower():
                return t.id
        return None

    async def process_stream(
        self,
        user_message: str,
        user_id: str,
        conversation_history: list = None
    ) -> AsyncGenerator[str, None]:
        """Process a message and stream ChatKit-formatted SSE events.

        Args:
            user_message: The user's message
            user_id: The authenticated user ID
            conversation_history: Optional conversation history

        Yields:
            SSE-formatted event strings
        """
        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # Add the current user message
        messages.append({"role": "user", "content": user_message})

        # Generate response ID
        response_id = f"resp_{uuid.uuid4().hex[:24]}"
        message_id = f"msg_{uuid.uuid4().hex[:24]}"

        try:
            # Call OpenAI with streaming
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=CHATKIT_TOOLS,
                tool_choice="auto",
                stream=True
            )

            # Track the response content
            full_content = ""
            tool_calls = {}
            current_tool_call_id = None

            for chunk in response:
                delta = chunk.choices[0].delta if chunk.choices else None
                if not delta:
                    continue

                # Handle content streaming
                if delta.content:
                    full_content += delta.content

                    # Emit content delta event
                    event_data = {
                        "type": "response.output_text.delta",
                        "delta": delta.content,
                        "response_id": response_id,
                        "item_id": message_id
                    }
                    yield f"event: response.output_text.delta\ndata: {json.dumps(event_data)}\n\n"

                # Handle tool calls
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        tc_id = tc.id or current_tool_call_id
                        if tc.id:
                            current_tool_call_id = tc.id
                            tool_calls[tc_id] = {
                                "id": tc_id,
                                "name": tc.function.name if tc.function else "",
                                "arguments": ""
                            }
                        if tc.function and tc.function.arguments:
                            if tc_id in tool_calls:
                                tool_calls[tc_id]["arguments"] += tc.function.arguments

                # Check for finish reason
                if chunk.choices[0].finish_reason:
                    if chunk.choices[0].finish_reason == "tool_calls":
                        # Execute tool calls
                        tool_results = []
                        for tc_id, tc_data in tool_calls.items():
                            try:
                                args = json.loads(tc_data["arguments"]) if tc_data["arguments"] else {}
                            except json.JSONDecodeError:
                                args = {}

                            result = self._execute_tool(tc_data["name"], args, user_id)
                            tool_results.append({
                                "tool_call_id": tc_id,
                                "role": "tool",
                                "content": result
                            })

                        # Make a follow-up call with tool results
                        messages.append({
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": tc_id,
                                    "type": "function",
                                    "function": {
                                        "name": tc_data["name"],
                                        "arguments": tc_data["arguments"]
                                    }
                                }
                                for tc_id, tc_data in tool_calls.items()
                            ]
                        })
                        for tr in tool_results:
                            messages.append(tr)

                        # Get final response
                        final_response = self.client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            stream=True
                        )

                        for final_chunk in final_response:
                            final_delta = final_chunk.choices[0].delta if final_chunk.choices else None
                            if final_delta and final_delta.content:
                                full_content += final_delta.content
                                event_data = {
                                    "type": "response.output_text.delta",
                                    "delta": final_delta.content,
                                    "response_id": response_id,
                                    "item_id": message_id
                                }
                                yield f"event: response.output_text.delta\ndata: {json.dumps(event_data)}\n\n"

            # Emit completion events
            done_event = {
                "type": "response.output_text.done",
                "text": full_content,
                "response_id": response_id,
                "item_id": message_id
            }
            yield f"event: response.output_text.done\ndata: {json.dumps(done_event)}\n\n"

            response_done = {
                "type": "response.done",
                "response_id": response_id
            }
            yield f"event: response.done\ndata: {json.dumps(response_done)}\n\n"

        except Exception as e:
            # Emit error event
            error_event = {
                "type": "error",
                "error": {
                    "message": str(e),
                    "type": "server_error"
                }
            }
            yield f"event: error\ndata: {json.dumps(error_event)}\n\n"


# Singleton instance
_server: Optional[ChatKitServer] = None


def get_chatkit_server() -> ChatKitServer:
    """Get or create the ChatKit server instance."""
    global _server
    if _server is None:
        _server = ChatKitServer()
    return _server
