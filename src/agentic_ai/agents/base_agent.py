"""
Base AI Agent class for multi-agent orchestration.

Defines the core interface and common functionality for all agents.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .memory_manager import MemoryManager

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Represents a message in agent communication."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class AgentTask:
    """Represents a task for an agent to execute."""

    task_id: str
    description: str
    objective: str
    context: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, in_progress, completed, failed

    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "objective": self.objective,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(
        self,
        name: str,
        role: str,
        description: str,
        bedrock_service: Any,
        enable_memory: bool = True,
        max_iterations: int = 10,
        temperature: float = 0.7,
    ):
        """
        Initialize a base agent.

        Args:
            name: Agent name
            role: Agent role/function
            description: Agent description
            bedrock_service: Bedrock service instance
            enable_memory: Whether to enable conversation memory
            max_iterations: Maximum iterations for task execution
            temperature: Model temperature for creativity
        """
        self.name = name
        self.role = role
        self.description = description
        self.bedrock_service = bedrock_service
        self.max_iterations = max_iterations
        self.temperature = temperature

        self.message_history: list[AgentMessage] = []
        self.memory_manager = MemoryManager() if enable_memory else None

        logger.info(f"Initialized agent: {name} with role: {role}")

    @abstractmethod
    def execute_task(self, task: AgentTask) -> dict:
        """
        Execute a task.

        Args:
            task: Task to execute

        Returns:
            Result dictionary
        """
        pass

    @abstractmethod
    def plan(self, objective: str, context: dict) -> list[str]:
        """
        Create a plan for achieving an objective.

        Args:
            objective: The objective to plan for
            context: Context information

        Returns:
            List of action steps
        """
        pass

    def add_message(self, role: str, content: str, metadata: Optional[dict] = None) -> None:
        """
        Add a message to the conversation history.

        Args:
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional metadata
        """
        message = AgentMessage(role=role, content=content, metadata=metadata or {})
        self.message_history.append(message)

        if self.memory_manager:
            self.memory_manager.add_message(message)

        logger.debug(f"Agent {self.name} added message: {role}")

    def get_conversation_context(self, max_messages: Optional[int] = None) -> list[dict]:
        """
        Get conversation context for model invocation.

        Args:
            max_messages: Maximum number of messages to include

        Returns:
            List of message dictionaries for API call
        """
        messages = self.message_history
        if max_messages:
            messages = messages[-max_messages:]

        return [{"role": msg.role, "content": msg.content} for msg in messages]

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Returns:
            System prompt string
        """
        return f"""You are {self.name}, a specialized AI agent.
Role: {self.role}
Description: {self.description}

Guidelines:
- Provide clear, concise, and helpful responses
- Break down complex problems into steps
- Ask for clarification when needed
- Be honest about limitations
- Follow instructions carefully"""

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.message_history = []
        if self.memory_manager:
            self.memory_manager.clear()
        logger.info(f"Cleared history for agent: {self.name}")

    def get_agent_info(self) -> dict:
        """Get information about this agent.

        Returns:
            Agent information dictionary
        """
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "max_iterations": self.max_iterations,
            "temperature": self.temperature,
            "messages_count": len(self.message_history),
        }
