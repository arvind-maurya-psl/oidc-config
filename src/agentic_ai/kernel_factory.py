"""
Semantic Kernel factory for creating and configuring kernel instances.

Handles kernel initialization, plugin registration, and function setup.
"""

import logging

from semantic_kernel import Kernel

from .config import get_config
from .services.bedrock_service import BedrockService

logger = logging.getLogger(__name__)


class KernelFactory:
    """Factory for creating configured Semantic Kernel instances."""

    def __init__(self):
        """Initialize the kernel factory."""
        self.config = get_config()
        self.bedrock_service = BedrockService()

    def create_kernel(self, include_plugins: bool = True) -> Kernel:
        """
        Create and configure a Semantic Kernel instance.

        Args:
            include_plugins: Whether to load default plugins

        Returns:
            Configured Kernel instance
        """
        kernel = Kernel()

        # Add chat completion service (using OpenAI for Semantic Kernel compatibility)
        # In production, you would create a custom connector for Bedrock
        # For now, we'll use the Bedrock service directly via agents

        logger.info("Created Semantic Kernel instance")

        if include_plugins:
            self._register_default_plugins(kernel)

        return kernel

    def _register_default_plugins(self, kernel: Kernel) -> None:
        """
        Register default plugins with the kernel.

        Args:
            kernel: The kernel instance to register plugins with
        """
        # Plugin registration will be done by the Agent implementation
        # This method is a placeholder for future plugin registration
        logger.debug("Default plugins registration placeholder")

    def get_bedrock_service(self) -> BedrockService:
        """
        Get the Bedrock service instance.

        Returns:
            BedrockService instance
        """
        return self.bedrock_service
