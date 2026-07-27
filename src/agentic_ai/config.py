"""
Configuration management for the Agentic AI application.

Handles environment variables, credential loading, and configuration validation.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


# Load environment variables from .env file if it exists
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


@dataclass
class AWSConfig:
    """AWS Bedrock and authentication configuration."""

    region: str = field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))
    bedrock_model_id: str = field(
        default_factory=lambda: os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
        )
    )
    bedrock_endpoint: Optional[str] = field(default_factory=lambda: os.getenv("BEDROCK_ENDPOINT"))
    max_retries: int = field(default_factory=lambda: int(os.getenv("AWS_MAX_RETRIES", "3")))
    timeout_seconds: int = field(default_factory=lambda: int(os.getenv("AWS_TIMEOUT_SECONDS", "300")))

    def validate(self) -> None:
        """Validate AWS configuration."""
        if not self.region:
            raise ValueError("AWS_REGION environment variable is required")
        if not self.bedrock_model_id:
            raise ValueError("BEDROCK_MODEL_ID environment variable is required")


@dataclass
class SemanticKernelConfig:
    """Semantic Kernel configuration."""

    log_enabled: bool = os.getenv("SK_LOG_ENABLED", "true").lower() == "true"
    log_level: str = os.getenv("SK_LOG_LEVEL", "INFO")
    function_call_retry_max_attempts: int = int(os.getenv("SK_FUNCTION_CALL_RETRY_MAX_ATTEMPTS", "3"))
    timeout_seconds: int = int(os.getenv("SK_TIMEOUT_SECONDS", "300"))

    def validate(self) -> None:
        """Validate Semantic Kernel configuration."""
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.log_level}. Must be one of {valid_log_levels}")


@dataclass
class AgentConfig:
    """AI Agent configuration."""

    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
    temperature: float = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
    timeout_seconds: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "600"))
    enable_memory: bool = os.getenv("AGENT_ENABLE_MEMORY", "true").lower() == "true"
    memory_type: str = os.getenv("AGENT_MEMORY_TYPE", "in_memory")  # in_memory or redis

    def validate(self) -> None:
        """Validate agent configuration."""
        if not 0 <= self.temperature <= 2:
            raise ValueError("AGENT_TEMPERATURE must be between 0 and 2")
        if self.max_iterations < 1:
            raise ValueError("AGENT_MAX_ITERATIONS must be at least 1")
        if self.memory_type not in {"in_memory", "redis"}:
            raise ValueError("AGENT_MEMORY_TYPE must be 'in_memory' or 'redis'")


@dataclass
class AppConfig:
    """Main application configuration."""

    env: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    aws: AWSConfig = None
    semantic_kernel: SemanticKernelConfig = None
    agent: AgentConfig = None

    def __post_init__(self) -> None:
        """Initialize sub-configurations after dataclass initialization."""
        if self.aws is None:
            self.aws = AWSConfig()
        if self.semantic_kernel is None:
            self.semantic_kernel = SemanticKernelConfig()
        if self.agent is None:
            self.agent = AgentConfig()

    def validate(self) -> None:
        """Validate all configuration sections."""
        if self.env not in {"development", "testing", "staging", "production"}:
            raise ValueError(f"Invalid environment: {self.env}")

        self.aws.validate()
        self.semantic_kernel.validate()
        self.agent.validate()

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        config = cls()
        config.validate()
        return config


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config


def reset_config() -> None:
    """Reset the global configuration instance (useful for testing)."""
    global _config
    _config = None
