"""
Memory management for agents and conversations.

Handles conversation history, context retention, and memory operations.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Represents an entry in agent memory."""

    timestamp: datetime
    agent_name: str
    content: str
    message_type: str  # "user", "assistant", "system"
    metadata: dict

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "content": self.content,
            "message_type": self.message_type,
            "metadata": self.metadata,
        }


class MemoryManager:
    """Manages agent memory and conversation history."""

    def __init__(self, max_memory_entries: int = 1000, retention_days: int = 30):
        """
        Initialize memory manager.

        Args:
            max_memory_entries: Maximum number of entries to keep
            retention_days: Number of days to retain entries
        """
        self.max_memory_entries = max_memory_entries
        self.retention_days = retention_days
        self.memory: list[MemoryEntry] = []
        logger.info("Initialized MemoryManager")

    def add_message(self, message: "AgentMessage") -> None:  # noqa: F821
        """
        Add a message to memory.

        Args:
            message: Message to add
        """
        entry = MemoryEntry(
            timestamp=message.timestamp,
            agent_name=getattr(message, "agent_name", "unknown"),
            content=message.content,
            message_type=message.role,
            metadata=message.metadata,
        )
        self.memory.append(entry)
        self._cleanup_memory()
        logger.debug("Added message to memory")

    def get_recent_messages(self, limit: int = 10) -> list[dict]:
        """
        Get recent messages from memory.

        Args:
            limit: Number of messages to retrieve

        Returns:
            List of message dictionaries
        """
        recent = self.memory[-limit:] if self.memory else []
        return [m.to_dict() for m in recent]

    def search_memory(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Search memory for entries matching query.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of matching entries
        """
        query_lower = query.lower()
        results = [
            m.to_dict()
            for m in self.memory
            if query_lower in m.content.lower()
        ]
        return results[:max_results]

    def get_context_window(self, max_age_hours: int = 24) -> list[dict]:
        """
        Get context within a time window.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            List of entries within the time window
        """
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        entries = [m for m in self.memory if m.timestamp > cutoff]
        return [m.to_dict() for m in entries]

    def clear(self) -> None:
        """Clear all memory."""
        self.memory.clear()
        logger.info("Cleared all memory")

    def _cleanup_memory(self) -> None:
        """Remove old entries if memory exceeds limits."""
        # Remove entries older than retention period
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        self.memory = [m for m in self.memory if m.timestamp > cutoff]

        # Keep only max entries
        if len(self.memory) > self.max_memory_entries:
            self.memory = self.memory[-self.max_memory_entries :]

    def get_memory_stats(self) -> dict:
        """Get statistics about memory usage.

        Returns:
            Dictionary with memory statistics
        """
        if not self.memory:
            return {
                "total_entries": 0,
                "oldest_entry": None,
                "newest_entry": None,
            }

        return {
            "total_entries": len(self.memory),
            "oldest_entry": self.memory[0].timestamp.isoformat(),
            "newest_entry": self.memory[-1].timestamp.isoformat(),
            "message_types": self._count_message_types(),
        }

    def _count_message_types(self) -> dict:
        """Count messages by type."""
        counts = {}
        for entry in self.memory:
            counts[entry.message_type] = counts.get(entry.message_type, 0) + 1
        return counts
