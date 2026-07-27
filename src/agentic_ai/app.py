"""
Main application entry point for the Agentic AI system.

Demonstrates usage of the Semantic Kernel, Bedrock integration, and multi-agent orchestration.
"""

import logging
from uuid import uuid4

from .agents import (
    AgentCoordinator,
    AgentTask,
    AnalyticsAgent,
    ContentGenerationAgent,
    CustomerServiceAgent,
)
from .config import get_config
from .kernel_factory import KernelFactory
from .utils import setup_logging

logger = logging.getLogger(__name__)


class AgenticAIApplication:
    """Main application for multi-agent Agentic AI system."""

    def __init__(self):
        """Initialize the Agentic AI application."""
        self.config = get_config()
        self.kernel_factory = KernelFactory()
        self.bedrock_service = self.kernel_factory.get_bedrock_service()

        # Initialize agents
        self.agents = {
            "analytics": AnalyticsAgent(self.bedrock_service),
            "customer_service": CustomerServiceAgent(self.bedrock_service),
            "content_generation": ContentGenerationAgent(self.bedrock_service),
        }

        # Initialize coordinator
        self.coordinator = AgentCoordinator(self.agents)

        logger.info("Initialized AgenticAIApplication")

    def execute_task(self, description: str, objective: str, agent_name: str = None) -> dict:
        """
        Execute a task with an agent.

        Args:
            description: Task description
            objective: Task objective
            agent_name: Specific agent to use (if None, auto-route)

        Returns:
            Task execution result
        """
        task = AgentTask(
            task_id=str(uuid4()),
            description=description,
            objective=objective,
        )

        if agent_name:
            return self.coordinator.delegate_task(task, agent_name)
        else:
            return self.coordinator.route_task(task)

    def execute_workflow(self, objective: str, tasks_data: list[dict]) -> dict:
        """
        Execute a workflow with multiple tasks.

        Args:
            objective: Workflow objective
            tasks_data: List of task dictionaries with 'description' and 'objective'

        Returns:
            Workflow execution result
        """
        tasks = [
            AgentTask(
                task_id=str(uuid4()),
                description=task_data["description"],
                objective=task_data["objective"],
            )
            for task_data in tasks_data
        ]

        return self.coordinator.execute_workflow(objective, tasks)

    def collaborate_agents(
        self,
        primary_agent: str,
        secondary_agents: list[str],
        description: str,
        objective: str,
    ) -> dict:
        """
        Execute a task with agent collaboration.

        Args:
            primary_agent: Primary agent name
            secondary_agents: List of secondary agent names
            description: Task description
            objective: Task objective

        Returns:
            Collaboration result
        """
        task = AgentTask(
            task_id=str(uuid4()),
            description=description,
            objective=objective,
        )

        return self.coordinator.agent_collaboration(
            primary_agent, secondary_agents, task
        )

    def get_system_info(self) -> dict:
        """Get system information.

        Returns:
            Dictionary with system information
        """
        return {
            "bedrock_model": self.bedrock_service.get_model_info(),
            "agents": self.coordinator.get_agent_stats(),
            "config": {
                "environment": self.config.env,
                "debug": self.config.debug,
                "log_level": self.config.log_level,
            },
        }


def main():
    """Main entry point for demonstration."""
    # Setup logging
    setup_logging()

    # Create application
    app = AgenticAIApplication()

    logger.info("Starting Agentic AI Application")

    # Example 1: Analytics task
    logger.info("=== Example 1: Analytics Task ===")
    analytics_result = app.execute_task(
        description="Analyze Q3 sales data for trends and patterns",
        objective="Identify key sales trends and growth areas",
        agent_name="analytics",
    )
    logger.info(f"Analytics result: {analytics_result}")

    # Example 2: Content generation task
    logger.info("=== Example 2: Content Generation Task ===")
    content_result = app.execute_task(
        description="Write a professional blog post about AI in enterprise",
        objective="Create engaging content for technical audience",
        agent_name="content_generation",
    )
    logger.info(f"Content result: {content_result}")

    # Example 3: Auto-routed task
    logger.info("=== Example 3: Auto-routed Task ===")
    auto_result = app.execute_task(
        description="Customer reported login issues, needs support",
        objective="Resolve customer authentication problem",
    )
    logger.info(f"Auto-routed result: {auto_result}")

    # Example 4: Workflow
    logger.info("=== Example 4: Workflow Execution ===")
    workflow_result = app.execute_workflow(
        objective="Comprehensive market analysis",
        tasks_data=[
            {
                "description": "Analyze competitor pricing strategies",
                "objective": "Identify pricing opportunities",
            },
            {
                "description": "Generate market entry strategy document",
                "objective": "Create actionable strategy",
            },
        ],
    )
    logger.info(f"Workflow result: {workflow_result}")

    # Example 5: Agent collaboration
    logger.info("=== Example 5: Agent Collaboration ===")
    collab_result = app.collaborate_agents(
        primary_agent="content_generation",
        secondary_agents=["analytics"],
        description="Generate a data-driven market analysis report",
        objective="Create comprehensive report with insights",
    )
    logger.info(f"Collaboration result: {collab_result}")

    # Print system info
    logger.info("=== System Information ===")
    sys_info = app.get_system_info()
    logger.info(f"System Info: {sys_info}")


if __name__ == "__main__":
    main()
