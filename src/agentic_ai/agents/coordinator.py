"""
Multi-agent orchestrator for coordinating multiple agents.

Handles agent selection, task delegation, and result aggregation.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .base_agent import AgentTask, BaseAgent

logger = logging.getLogger(__name__)


@dataclass
class TaskAllocation:
    """Represents a task allocation to an agent."""

    task_id: str
    agent_name: str
    allocated_at: datetime
    status: str = "pending"  # pending, executing, completed, failed
    result: Optional[dict] = None
    error: Optional[str] = None


class AgentCoordinator:
    """Orchestrates communication and task delegation between multiple agents."""

    def __init__(self, agents: dict[str, BaseAgent]):
        """
        Initialize the agent coordinator.

        Args:
            agents: Dictionary mapping agent names to BaseAgent instances
        """
        self.agents = agents
        self.task_allocations: list[TaskAllocation] = []
        self.execution_log: list[dict] = []

        logger.info(f"Initialized AgentCoordinator with {len(agents)} agents")
        for name in agents.keys():
            logger.info(f"  - {name}")

    def delegate_task(self, task: AgentTask, agent_name: str) -> dict:
        """
        Delegate a task to a specific agent.

        Args:
            task: Task to delegate
            agent_name: Name of the agent to handle the task

        Returns:
            Task execution result
        """
        if agent_name not in self.agents:
            error_msg = f"Agent '{agent_name}' not found"
            logger.error(error_msg)
            return {"status": "failed", "error": error_msg}

        agent = self.agents[agent_name]

        # Record allocation
        allocation = TaskAllocation(
            task_id=task.task_id,
            agent_name=agent_name,
            allocated_at=datetime.utcnow(),
        )

        logger.info(f"Delegating task {task.task_id} to agent: {agent_name}")

        try:
            result = agent.execute_task(task)
            allocation.status = "completed"
            allocation.result = result

            self.task_allocations.append(allocation)
            self._log_execution(task, agent_name, result)

            return result

        except Exception as e:
            logger.error(f"Task delegation failed: {e}")
            allocation.status = "failed"
            allocation.error = str(e)
            self.task_allocations.append(allocation)

            return {
                "status": "failed",
                "error": str(e),
            }

    def route_task(self, task: AgentTask) -> dict:
        """
        Automatically route a task to the most appropriate agent based on keywords.

        Args:
            task: Task to route

        Returns:
            Task execution result
        """
        agent_name = self._select_agent(task)
        return self.delegate_task(task, agent_name)

    def _select_agent(self, task: AgentTask) -> str:
        """
        Select the most appropriate agent for a task based on keywords.

        Args:
            task: Task to analyze

        Returns:
            Selected agent name
        """
        # Keyword-based routing
        description_lower = (task.description + " " + task.objective).lower()

        routing_rules = {
            "analytics": ["analyze", "data", "trend", "stat", "report", "insight"],
            "customer": ["customer", "support", "help", "issue", "complaint", "inquiry"],
            "content": ["write", "generate", "create", "article", "email", "copy", "blog"],
        }

        scores = {}
        for agent_key, keywords in routing_rules.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            # Match agent name from dictionary
            for agent_name in self.agents.keys():
                if agent_key.lower() in agent_name.lower():
                    scores[agent_name] = score

        # Return agent with highest match score
        if scores:
            best_agent = max(scores, key=scores.get)
            logger.info(f"Routed task to agent: {best_agent} (score: {scores[best_agent]})")
            return best_agent

        # Default to first agent if no match
        default_agent = list(self.agents.keys())[0]
        logger.warning(f"No routing match found, using default agent: {default_agent}")
        return default_agent

    def execute_workflow(self, objective: str, tasks: list[AgentTask]) -> dict:
        """
        Execute a workflow consisting of multiple tasks.

        Args:
            objective: Overall workflow objective
            tasks: List of tasks to execute

        Returns:
            Workflow result with individual task results
        """
        logger.info(f"Starting workflow with {len(tasks)} tasks: {objective}")

        results = []
        for task in tasks:
            result = self.route_task(task)
            results.append(result)

        workflow_result = {
            "objective": objective,
            "task_count": len(tasks),
            "completed_count": sum(1 for r in results if r.get("status") == "completed"),
            "failed_count": sum(1 for r in results if r.get("status") == "failed"),
            "results": results,
        }

        logger.info(f"Workflow completed: {workflow_result['completed_count']}/{len(tasks)} tasks")
        return workflow_result

    def agent_collaboration(
        self, primary_agent_name: str, secondary_agents: list[str], task: AgentTask
    ) -> dict:
        """
        Execute a task with agent collaboration.

        Allows a primary agent to request input from secondary agents.

        Args:
            primary_agent_name: Primary agent handling the task
            secondary_agents: List of secondary agents for consultation
            task: Task to execute

        Returns:
            Collaboration result
        """
        if primary_agent_name not in self.agents:
            error_msg = f"Primary agent '{primary_agent_name}' not found"
            logger.error(error_msg)
            return {"status": "failed", "error": error_msg}

        logger.info(f"Starting agent collaboration: {primary_agent_name} with {secondary_agents}")

        # Primary agent handles main task
        primary_result = self.delegate_task(task, primary_agent_name)

        # Gather input from secondary agents
        secondary_results = {}
        for agent_name in secondary_agents:
            if agent_name in self.agents:
                # Create consultation task for secondary agent
                consultation_task = AgentTask(
                    task_id=f"{task.task_id}_consultation_{agent_name}",
                    description=f"Provide expert opinion on: {task.description}",
                    objective=f"Consult on: {task.objective}",
                    context=task.context,
                )
                secondary_results[agent_name] = self.delegate_task(
                    consultation_task, agent_name
                )

        return {
            "primary_agent": primary_agent_name,
            "primary_result": primary_result,
            "secondary_consultations": secondary_results,
        }

    def get_agent_stats(self) -> dict:
        """
        Get statistics about all registered agents.

        Returns:
            Dictionary with agent statistics
        """
        stats = {}
        for name, agent in self.agents.items():
            stats[name] = agent.get_agent_info()

        return stats

    def get_execution_history(self, limit: Optional[int] = None) -> list[dict]:
        """
        Get execution history.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of execution log entries
        """
        history = self.execution_log
        if limit:
            history = history[-limit:]
        return history

    def _log_execution(self, task: AgentTask, agent_name: str, result: dict) -> None:
        """
        Log task execution.

        Args:
            task: Executed task
            agent_name: Agent that executed the task
            result: Execution result
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task.task_id,
            "agent_name": agent_name,
            "status": result.get("status"),
            "task_objective": task.objective,
        }
        self.execution_log.append(log_entry)
