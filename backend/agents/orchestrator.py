"""Orchestrator Agent - Routes user intents to specialized subagents."""

import os
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from openai import OpenAI

from .base import BaseAgent, AgentResult
from .crud_agent import CRUDAgent
from .query_agent import QueryAgent
from .completion_agent import CompletionAgent
from .context_agent import ContextAgent
from mcp_server import MCPTools, TaskNotFoundError, UnauthorizedError
from skills import (
    context_builder, MessageContext,
    id_resolver, TaskReference,
    error_handler,
)


@dataclass
class OrchestrationResult:
    """Result from orchestrator processing."""
    response: str
    agent_used: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    success: bool = True


class Orchestrator:
    """Main orchestrator that routes user requests to specialized subagents.

    The orchestrator:
    1. Analyzes user input to detect intent
    2. Routes to the appropriate subagent
    3. Falls back to OpenAI for complex/ambiguous requests
    4. Manages conversation context
    """

    def __init__(self, user_id: str):
        """Initialize orchestrator with user context.

        Args:
            user_id: The user ID for all operations
        """
        self.user_id = user_id

        # Initialize subagents
        self.crud_agent = CRUDAgent(user_id)
        self.query_agent = QueryAgent(user_id)
        self.completion_agent = CompletionAgent(user_id)
        self.context_agent = ContextAgent(user_id)

        # Agent priority order for intent matching
        self.agents: List[BaseAgent] = [
            self.completion_agent,  # Check completion first (specific)
            self.crud_agent,        # Then CRUD operations
            self.query_agent,       # Then queries
            self.context_agent,     # Finally context/general
        ]

        # OpenAI client (lazy initialization)
        self._openai_client: Optional[OpenAI] = None

    @property
    def openai_client(self) -> OpenAI:
        """Lazy-initialize OpenAI client."""
        if self._openai_client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self._openai_client = OpenAI(api_key=api_key)
        return self._openai_client

    def process(
        self,
        user_message: str,
        conversation_history: Optional[List[MessageContext]] = None
    ) -> OrchestrationResult:
        """Process a user message and return a response.

        Args:
            user_message: The user's message
            conversation_history: Optional conversation history

        Returns:
            OrchestrationResult with response and metadata
        """
        if not user_message.strip():
            return OrchestrationResult(
                response="I didn't catch that. How can I help you with your tasks?",
                success=True
            )

        conversation_history = conversation_history or []

        # Try rule-based routing first
        result = self._try_rule_based_routing(user_message, conversation_history)
        if result:
            return result

        # Fall back to OpenAI for complex requests
        return self._process_with_openai(user_message, conversation_history)

    def _try_rule_based_routing(
        self,
        user_message: str,
        conversation_history: List[MessageContext]
    ) -> Optional[OrchestrationResult]:
        """Try to route using rule-based intent detection.

        Args:
            user_message: The user's message
            conversation_history: Conversation history

        Returns:
            OrchestrationResult if handled, None otherwise
        """
        message_lower = user_message.lower().strip()

        # Try each agent in priority order
        for agent in self.agents:
            if agent.can_handle(message_lower):
                result = agent.execute(
                    intent=message_lower,
                    user_input=user_message,
                    conversation_history=conversation_history
                )

                if result.success:
                    return OrchestrationResult(
                        response=result.message,
                        agent_used=agent.name,
                        success=True
                    )

        return None

    def _process_with_openai(
        self,
        user_message: str,
        conversation_history: List[MessageContext]
    ) -> OrchestrationResult:
        """Process message using OpenAI with function calling.

        Args:
            user_message: The user's message
            conversation_history: Conversation history

        Returns:
            OrchestrationResult with AI-generated response
        """
        try:
            # Build context for OpenAI
            built_context = context_builder.execute(
                conversation_history=conversation_history,
                user_message=user_message,
                include_system_prompt=True
            )

            # Get tool definitions
            tools = MCPTools.get_tool_definitions()

            # Call OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=built_context.messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=1000
            )

            message = response.choices[0].message

            # Check if OpenAI wants to call tools
            if message.tool_calls:
                return self._handle_tool_calls(message.tool_calls, user_message)

            # Return the text response
            return OrchestrationResult(
                response=message.content or "I'm not sure how to help with that.",
                agent_used="openai",
                success=True
            )

        except Exception as e:
            error_response = error_handler.execute(error=e)
            return OrchestrationResult(
                response=error_handler.format_response(error_response),
                success=False
            )

    def _handle_tool_calls(
        self,
        tool_calls: List,
        original_message: str
    ) -> OrchestrationResult:
        """Handle OpenAI tool calls.

        Args:
            tool_calls: List of tool calls from OpenAI
            original_message: The original user message

        Returns:
            OrchestrationResult with tool execution results
        """
        results = []
        tool_call_info = []

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            tool_call_info.append({
                "tool": tool_name,
                "arguments": arguments
            })

            try:
                # Execute the tool
                result = MCPTools.execute_tool(
                    tool_name=tool_name,
                    user_id=self.user_id,
                    arguments=arguments
                )

                # Format result for response
                results.append(self._format_tool_result(tool_name, result))

            except TaskNotFoundError as e:
                error_response = error_handler.execute(error=e)
                results.append(error_handler.format_response(error_response))

            except UnauthorizedError as e:
                error_response = error_handler.execute(error=e)
                results.append(error_handler.format_response(error_response))

            except Exception as e:
                error_response = error_handler.execute(error=e)
                results.append(error_handler.format_response(error_response))

        # Combine results
        response = "\n".join(results) if results else "Operation completed."

        return OrchestrationResult(
            response=response,
            agent_used="openai",
            tool_calls=tool_call_info,
            success=True
        )

    def _format_tool_result(self, tool_name: str, result) -> str:
        """Format a tool result into a human-readable message.

        Args:
            tool_name: Name of the tool that was called
            result: The tool's output object

        Returns:
            Formatted string message
        """
        from skills import confirmation_generator, TaskInfo

        if tool_name == "add_task":
            task_info = TaskInfo(id=result.task_id, title=result.title)
            return confirmation_generator.execute("created", task=task_info)

        elif tool_name == "list_tasks":
            task_infos = [
                TaskInfo(
                    id=t.id,
                    title=t.title,
                    description=t.description,
                    completed=t.completed
                )
                for t in result.tasks
            ]
            msg = confirmation_generator.execute(
                "listed",
                tasks=task_infos,
                filter_applied=result.filter_applied
            )
            # Add task list
            if result.tasks:
                lines = []
                for t in result.tasks:
                    status = "[x]" if t.completed else "[ ]"
                    lines.append(f"{status} {t.title}")
                msg += "\n\n" + "\n".join(lines)
            return msg

        elif tool_name == "complete_task":
            task_info = TaskInfo(id=result.task_id, title=result.title)
            action = "already_completed" if result.status == "already_completed" else "completed"
            return confirmation_generator.execute(action, task=task_info)

        elif tool_name == "delete_task":
            task_info = TaskInfo(id=result.task_id, title=result.title)
            return confirmation_generator.execute("deleted", task=task_info)

        elif tool_name == "update_task":
            task_info = TaskInfo(id=result.task_id, title=result.title)
            return confirmation_generator.execute(
                "updated",
                task=task_info,
                changes=result.changes
            )

        else:
            return f"Completed {tool_name} operation."


# Convenience function for simple usage
def process_message(
    user_id: str,
    message: str,
    conversation_history: Optional[List[MessageContext]] = None
) -> OrchestrationResult:
    """Process a user message through the orchestrator.

    Args:
        user_id: The user's ID
        message: The user's message
        conversation_history: Optional conversation history

    Returns:
        OrchestrationResult with response
    """
    orchestrator = Orchestrator(user_id)
    return orchestrator.process(message, conversation_history)
