"""Skills Module - Reusable AI agent skills for task management."""

from .base import BaseSkill
from .task_parser import TaskParserSkill, ParsedTask, task_parser
from .id_resolver import IDResolverSkill, ResolvedTask, TaskReference, id_resolver
from .filter_mapper import FilterMapperSkill, FilterParams, filter_mapper
from .confirmation_generator import ConfirmationGeneratorSkill, TaskInfo, confirmation_generator
from .error_handler import ErrorHandlerSkill, ErrorResponse, error_handler
from .context_builder import ContextBuilderSkill, MessageContext, BuiltContext, context_builder

__all__ = [
    # Base
    "BaseSkill",

    # Task Parser
    "TaskParserSkill",
    "ParsedTask",
    "task_parser",

    # ID Resolver
    "IDResolverSkill",
    "ResolvedTask",
    "TaskReference",
    "id_resolver",

    # Filter Mapper
    "FilterMapperSkill",
    "FilterParams",
    "filter_mapper",

    # Confirmation Generator
    "ConfirmationGeneratorSkill",
    "TaskInfo",
    "confirmation_generator",

    # Error Handler
    "ErrorHandlerSkill",
    "ErrorResponse",
    "error_handler",

    # Context Builder
    "ContextBuilderSkill",
    "MessageContext",
    "BuiltContext",
    "context_builder",
]
