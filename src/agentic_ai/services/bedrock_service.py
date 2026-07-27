"""
AWS Bedrock service for LLM interactions.

Handles initialization, model invocation, streaming, and error handling for AWS Bedrock.
"""

import json
import logging
from typing import Any, Dict, Generator, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ..config import get_config

logger = logging.getLogger(__name__)


class BedrockServiceError(Exception):
    """Base exception for Bedrock service errors."""

    pass


class BedrockModelError(BedrockServiceError):
    """Exception raised when model invocation fails."""

    pass


class BedrockService:
    """Service for interacting with AWS Bedrock models."""

    def __init__(self, region: Optional[str] = None, model_id: Optional[str] = None):
        """
        Initialize Bedrock service.

        Args:
            region: AWS region (uses config if not provided)
            model_id: Bedrock model ID (uses config if not provided)
        """
        config = get_config()
        self.region = region or config.aws.region
        self.model_id = model_id or config.aws.bedrock_model_id
        self.endpoint = config.aws.bedrock_endpoint
        self.max_retries = config.aws.max_retries
        self.timeout = config.aws.timeout_seconds

        self.client = self._create_client()
        logger.info(f"Initialized BedrockService with model: {self.model_id} in region: {self.region}")

    def _create_client(self) -> Any:
        """Create and return a Bedrock runtime client."""
        try:
            if self.endpoint:
                return boto3.client(
                    "bedrock-runtime",
                    region_name=self.region,
                    endpoint_url=self.endpoint,
                )
            else:
                return boto3.client(
                    "bedrock-runtime",
                    region_name=self.region,
                )
        except BotoCoreError as e:
            logger.error(f"Failed to create Bedrock client: {e}")
            raise BedrockServiceError(f"Failed to initialize Bedrock client: {e}") from e

    def invoke_model(
        self,
        messages: list[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Invoke a Bedrock model with messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-2)
            system_prompt: Optional system prompt

        Returns:
            Model response text

        Raises:
            BedrockModelError: If model invocation fails
        """
        try:
            # Prepare the request body based on Claude model format
            body = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": min(max(temperature, 0), 2),  # Clamp between 0 and 2
            }

            # Add system prompt if provided
            if system_prompt:
                body["system"] = system_prompt

            logger.debug(f"Invoking Bedrock model {self.model_id} with {len(messages)} messages")

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
            )

            # Parse response
            response_body = json.loads(response["body"].read().decode("utf-8"))

            # Extract text from response (Claude format)
            if "content" in response_body and len(response_body["content"]) > 0:
                return response_body["content"][0]["text"]

            logger.warning("Unexpected Bedrock response format")
            return ""

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            logger.error(f"Bedrock client error ({error_code}): {error_msg}")
            raise BedrockModelError(f"Bedrock API error: {error_msg}") from e
        except (BotoCoreError, json.JSONDecodeError) as e:
            logger.error(f"Bedrock service error: {e}")
            raise BedrockModelError(f"Failed to invoke Bedrock model: {e}") from e

    def invoke_model_streaming(
        self,
        messages: list[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """
        Invoke a Bedrock model with streaming response.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-2)
            system_prompt: Optional system prompt

        Yields:
            Streamed text chunks from the model

        Raises:
            BedrockModelError: If model invocation fails
        """
        try:
            # Prepare the request body
            body = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": min(max(temperature, 0), 2),
            }

            if system_prompt:
                body["system"] = system_prompt

            logger.debug(f"Invoking Bedrock model {self.model_id} with streaming")

            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(body),
            )

            # Process stream events
            for event in response.get("body", []):
                if "chunk" in event:
                    chunk = json.loads(event["chunk"]["bytes"].decode("utf-8"))
                    if "delta" in chunk and "text" in chunk["delta"]:
                        yield chunk["delta"]["text"]

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            logger.error(f"Bedrock streaming error ({error_code}): {error_msg}")
            raise BedrockModelError(f"Bedrock streaming error: {error_msg}") from e
        except (BotoCoreError, json.JSONDecodeError) as e:
            logger.error(f"Bedrock service error during streaming: {e}")
            raise BedrockModelError(f"Bedrock streaming failed: {e}") from e

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the configured model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_id": self.model_id,
            "region": self.region,
            "endpoint": self.endpoint or "default",
        }
