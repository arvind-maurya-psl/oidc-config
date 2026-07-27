"""
Agentic AI Application using AWS Bedrock and Microsoft Semantic Kernel.

A production-grade enterprise AI application supporting multi-agent orchestration,
plugin architecture, and comprehensive logging and error handling.
"""

__version__ = "1.0.0"
__author__ = "Enterprise AI Team"

from .kernel_factory import KernelFactory
from .services.bedrock_service import BedrockService

__all__ = ["KernelFactory", "BedrockService"]
