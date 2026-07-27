"""
Specialized AI agents for different business domains.

Includes agents for analytics, customer service, and content generation.
"""

import logging

from .base_agent import AgentTask, BaseAgent

logger = logging.getLogger(__name__)


class AnalyticsAgent(BaseAgent):
    """Agent specialized in data analysis and business intelligence."""

    def __init__(self, bedrock_service, enable_memory: bool = True):
        """Initialize analytics agent."""
        super().__init__(
            name="Analytics Agent",
            role="Business Intelligence & Data Analysis",
            description="Analyzes data, generates insights, and creates reports",
            bedrock_service=bedrock_service,
            enable_memory=enable_memory,
            temperature=0.5,  # Lower temperature for analytical accuracy
        )

    def plan(self, objective: str, context: dict) -> list[str]:
        """Create a plan for analytics task."""
        plan_steps = [
            "Analyze the business question",
            "Identify relevant data sources",
            "Analyze data patterns and trends",
            "Generate insights and recommendations",
            "Create visualizations and reports",
        ]
        return plan_steps

    def execute_task(self, task: AgentTask) -> dict:
        """Execute an analytics task."""
        task.status = "in_progress"
        logger.info(f"Analytics Agent executing task: {task.task_id}")

        # Add task to conversation
        self.add_message(
            "user",
            f"Please analyze: {task.description}\nObjective: {task.objective}",
        )

        # Create prompt for Bedrock
        messages = self.get_conversation_context()
        system_prompt = self.get_system_prompt()

        try:
            # Invoke Bedrock model
            response = self.bedrock_service.invoke_model(
                messages=messages,
                max_tokens=2048,
                temperature=self.temperature,
                system_prompt=system_prompt,
            )

            # Add response to conversation
            self.add_message("assistant", response)

            result = {
                "task_id": task.task_id,
                "status": "completed",
                "analysis": response,
                "message_count": len(self.message_history),
            }

            task.status = "completed"
            return result

        except Exception as e:
            logger.error(f"Analytics Agent task failed: {e}")
            task.status = "failed"
            return {
                "task_id": task.task_id,
                "status": "failed",
                "error": str(e),
            }


class CustomerServiceAgent(BaseAgent):
    """Agent specialized in customer service and support."""

    def __init__(self, bedrock_service, enable_memory: bool = True):
        """Initialize customer service agent."""
        super().__init__(
            name="Customer Service Agent",
            role="Customer Support & Service",
            description="Provides customer support, handles inquiries, and resolves issues",
            bedrock_service=bedrock_service,
            enable_memory=enable_memory,
            temperature=0.7,
        )

    def plan(self, objective: str, context: dict) -> list[str]:
        """Create a plan for customer service task."""
        plan_steps = [
            "Understand customer inquiry",
            "Retrieve relevant customer information",
            "Identify issue category",
            "Provide solution or escalation path",
            "Confirm customer satisfaction",
        ]
        return plan_steps

    def execute_task(self, task: AgentTask) -> dict:
        """Execute a customer service task."""
        task.status = "in_progress"
        logger.info(f"Customer Service Agent executing task: {task.task_id}")

        self.add_message(
            "user",
            f"Customer inquiry: {task.description}\nContext: {task.context}",
        )

        messages = self.get_conversation_context()
        system_prompt = self.get_system_prompt()

        try:
            response = self.bedrock_service.invoke_model(
                messages=messages,
                max_tokens=1024,
                temperature=self.temperature,
                system_prompt=system_prompt,
            )

            self.add_message("assistant", response)

            result = {
                "task_id": task.task_id,
                "status": "completed",
                "response": response,
            }

            task.status = "completed"
            return result

        except Exception as e:
            logger.error(f"Customer Service Agent task failed: {e}")
            task.status = "failed"
            return {
                "task_id": task.task_id,
                "status": "failed",
                "error": str(e),
            }


class ContentGenerationAgent(BaseAgent):
    """Agent specialized in content creation and writing."""

    def __init__(self, bedrock_service, enable_memory: bool = True):
        """Initialize content generation agent."""
        super().__init__(
            name="Content Generation Agent",
            role="Content Creation & Writing",
            description="Generates high-quality content including articles, emails, and reports",
            bedrock_service=bedrock_service,
            enable_memory=enable_memory,
            temperature=0.8,  # Higher temperature for creativity
        )

    def plan(self, objective: str, context: dict) -> list[str]:
        """Create a plan for content generation task."""
        plan_steps = [
            "Understand content requirements",
            "Research relevant information",
            "Outline content structure",
            "Generate initial draft",
            "Review and refine content",
            "Optimize for audience and format",
        ]
        return plan_steps

    def execute_task(self, task: AgentTask) -> dict:
        """Execute a content generation task."""
        task.status = "in_progress"
        logger.info(f"Content Generation Agent executing task: {task.task_id}")

        self.add_message(
            "user",
            f"Create: {task.description}\nObjective: {task.objective}\nDetails: {task.context}",
        )

        messages = self.get_conversation_context()
        system_prompt = self.get_system_prompt()

        try:
            response = self.bedrock_service.invoke_model(
                messages=messages,
                max_tokens=4096,
                temperature=self.temperature,
                system_prompt=system_prompt,
            )

            self.add_message("assistant", response)

            result = {
                "task_id": task.task_id,
                "status": "completed",
                "content": response,
                "message_count": len(self.message_history),
            }

            task.status = "completed"
            return result

        except Exception as e:
            logger.error(f"Content Generation Agent task failed: {e}")
            task.status = "failed"
            return {
                "task_id": task.task_id,
                "status": "failed",
                "error": str(e),
            }
