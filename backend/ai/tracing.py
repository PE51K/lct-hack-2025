"""Module for setting up Langfuse tracing and callback handler for AI operations."""

import sys

# Add parent directory to sys.path for local imports
sys.path.insert(0, "..")

from langfuse._client.client import Langfuse
from langfuse.langchain import CallbackHandler

from core.settings import settings

langfuse_client = Langfuse(
    public_key=settings.ai.langfuse.public_key,
    secret_key=settings.ai.langfuse.secret_key,
    host=settings.ai.langfuse.base_url,
    tracing_enabled=settings.ai.langfuse.enabled,
)
langfuse_callback_handler = CallbackHandler(
    public_key=settings.ai.langfuse.public_key,
)


__all__ = ["langfuse_callback_handler", "langfuse_client"]
