"""
Lambda handler for AWS Lambda deployment.

This file allows the application to run on AWS Lambda.
"""

import json
from typing import Any, Dict

from agentic_ai.app import AgenticAIApplication
from agentic_ai.utils import format_response, setup_logging

# Setup logging
logger = setup_logging("lambda-handler")

# Initialize application (cold start optimization)
_app_instance = None


def get_app() -> AgenticAIApplication:
    """Get or create application instance."""
    global _app_instance
    if _app_instance is None:
        logger.info("Initializing Agentic AI application")
        _app_instance = AgenticAIApplication()
    return _app_instance


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for Agentic AI application.

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Lambda response
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Initialize app
        app = get_app()

        # Parse event
        action = event.get("action", "execute_task")
        description = event.get("description", "")
        objective = event.get("objective", "")
        agent_name = event.get("agent_name")

        # Execute action
        if action == "health":
            result = {"status": "healthy", "version": "1.0.0"}
        elif action == "execute_task":
            result = app.execute_task(description, objective, agent_name)
        elif action == "execute_workflow":
            tasks_data = event.get("tasks", [])
            result = app.execute_workflow(objective, tasks_data)
        elif action == "agent_info":
            result = app.get_system_info()
        else:
            return format_response("error", error=f"Unknown action: {action}")

        return format_response("success", data=result)

    except Exception as e:
        logger.error(f"Error handling request: {e}", exc_info=True)
        return format_response("error", error=str(e))


def lambda_handler_async(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Async version for long-running tasks.

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Lambda response
    """
    try:
        app = get_app()

        # Trigger background task
        description = event.get("description", "")
        objective = event.get("objective", "")

        # Execute asynchronously
        # In production, use SQS or Step Functions for async orchestration
        result = app.execute_task(description, objective)

        return format_response("success", data={"task_id": event.get("task_id"), "status": result["status"]})

    except Exception as e:
        logger.error(f"Error in async handler: {e}", exc_info=True)
        return format_response("error", error=str(e))
