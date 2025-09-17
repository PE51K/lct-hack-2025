"""
Main FastAPI application module.

This module sets up the FastAPI application with lifespan management,
logging, and API endpoints.
"""

import json
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Dict, Annotated
from enum import Enum

from pydantic import BaseModel
from langfuse._client.client import Langfuse
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import (
    AsyncConnectionPool, 
    AsyncPostgresSaver,
)
from langfuse.langchain import CallbackHandler
from langgraph.prebuilt import create_react_agent
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Add parent directory to sys.path for local imports
sys.path.insert(0, "..")

from core.logging import setup_logger
from core.settings import settings
from ai.llm import llm
from pydantic import BaseModel
from ai.agents.calculcator_agent import (
    calculator_agent_chat_prompt_template,
    calculator_agent_tools,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events.
    """
    # Setup logging
    app.state.logger = await setup_logger(__name__)

    # Startup
    await app.state.logger.info("Starting up application...")

    # Initialize LangFuse for tracing the UserCV."and monitoring
    await app.state.logger.info("Initializing LangFuse client for tracing...")
    app.state.langfuse_client = Langfuse(
        public_key=settings.ai.langfuse.public_key,
        secret_key=settings.ai.langfuse.secret_key,
        host=settings.ai.langfuse.base_url,
        tracing_enabled=settings.ai.langfuse.enabled,
    )
    app.state.langfuse_callback_handler = CallbackHandler(
        public_key=settings.ai.langfuse.public_key,
    )

    # Initialize agentic components
    await app.state.logger.info("Setting up PostgreSQL checkpointer for memory persistence...")
    async with AsyncConnectionPool(
        conninfo=settings.ai.langgraph_checkpointer.connection_string,
        kwargs={"autocommit": True},
    ) as pool:
        postgres_saver = AsyncPostgresSaver(pool)
        await postgres_saver.setup()

        # Set up calculator agent
        await app.state.logger.info("Setting up calculator agent...")
        app.state.calculator_agent = create_react_agent(
            model=llm,
            tools=calculator_agent_tools,
            prompt=calculator_agent_chat_prompt_template,
            checkpointer=postgres_saver,
        )

        # Finalize startup
        await app.state.logger.info("Application startup complete!")
        yield

    # Shutdown
    await app.state.logger.info("Application shutdown")
    await app.state.logger.shutdown()


# Initialize FastAPI application with lifespan management
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors.origins,
    allow_credentials=settings.app.cors.allow_credentials,
    allow_methods=settings.app.cors.allow_methods,
    allow_headers=settings.app.cors.allow_headers,
)


class ChatWithAgentRequest(BaseModel):
    message: str
    thread_id: str
    user_id: str


class AgentNameEnum(str):
    calculator = "calculator"


@app.post("/chat/{agent_name}")
async def chat_with_agent(agent_name: Annotated[str, AgentNameEnum], request: ChatWithAgentRequest = Form(...)) -> StreamingResponse:
    """
    Chat with the specified agent.

    Example response streaming JSON lines:
    ```
    {"message": {"content": "", "additional_kwargs": {"tool_calls": [{"index": 0, "id": "sum_numbers", "function": {"arguments": "{\"numbers\":[2,2]}", "name": "sum_numbers"}, "type": "function"}]}, "response_metadata": {"finish_reason": "tool_calls", "model_name": "gpt://b1gbknonr2fm4ss0se7a/yandexgpt"}, "type": "AIMessageChunk", "name": null, "id": "run--3cba6907-14b9-4e6d-bd0c-25b08defce11", "example": false, "tool_calls": [{"name": "sum_numbers", "args": {"numbers": [2, 2]}, "id": "sum_numbers", "type": "tool_call"}], "invalid_tool_calls": [], "usage_metadata": null, "tool_call_chunks": [{"name": "sum_numbers", "args": "{\"numbers\":[2,2]}", "id": "sum_numbers", "index": 0, "type": "tool_call_chunk"}]}, "metadata": {"langfuse_session_id": "132322312213344", "langfuse_user_id": "21321312323444", "langfuse_tags": ["chat", "fastapi", "agent", "calculator"], "thread_id": "132322312213344", "user_id": "21321312323444", "langgraph_step": 1, "langgraph_node": "agent", "langgraph_triggers": ["branch:to:agent"], "langgraph_path": ["__pregel_pull", "agent"], "langgraph_checkpoint_ns": "agent:6df49d2d-b200-b0cc-9203-31e209d3fb83", "checkpoint_ns": "agent:6df49d2d-b200-b0cc-9203-31e209d3fb83", "ls_provider": "openai", "ls_model_name": "gpt://b1gbknonr2fm4ss0se7a/yandexgpt", "ls_model_type": "chat", "ls_temperature": null}}
    {"message": {"content": "4.0", "additional_kwargs": {}, "response_metadata": {}, "type": "tool", "name": "sum_numbers", "id": "75b15edf-c77f-4042-8f52-8d153f6d50f6", "tool_call_id": "sum_numbers", "artifact": null, "status": "success"}, "metadata": {"langfuse_session_id": "132322312213344", "langfuse_user_id": "21321312323444", "langfuse_tags": ["chat", "fastapi", "agent", "calculator"], "thread_id": "132322312213344", "user_id": "21321312323444", "langgraph_step": 2, "langgraph_node": "tools", "langgraph_triggers": ["__pregel_push"], "langgraph_path": ["__pregel_push", 0, false], "langgraph_checkpoint_ns": "tools:d8618445-e763-954e-7b24-b86174d32525"}}
    {"message": {"content": "Two", "additional_kwargs": {}, "response_metadata": {}, "type": "AIMessageChunk", "name": null, "id": "run--ad573982-3ca5-4ce7-9f2a-1e9f0b5741a4", "example": false, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": null, "tool_call_chunks": []}, "metadata": {"langfuse_session_id": "132322312213344", "langfuse_user_id": "21321312323444", "langfuse_tags": ["chat", "fastapi", "agent", "calculator"], "thread_id": "132322312213344", "user_id": "21321312323444", "langgraph_step": 3, "langgraph_node": "agent", "langgraph_triggers": ["branch:to:agent"], "langgraph_path": ["__pregel_pull", "agent"], "langgraph_checkpoint_ns": "agent:63c327a0-f51a-6a2e-68ff-4a3b86f48d99", "checkpoint_ns": "agent:63c327a0-f51a-6a2e-68ff-4a3b86f48d99", "ls_provider": "openai", "ls_model_name": "gpt://b1gbknonr2fm4ss0se7a/yandexgpt", "ls_model_type": "chat", "ls_temperature": null}}
    {"message": {"content": " plus two, a simple quest,\nIn math's realm, a test of the best.\nThe sum is four, a fact so true,\nA number that's both", "additional_kwargs": {}, "response_metadata": {}, "type": "AIMessageChunk", "name": null, "id": "run--ad573982-3ca5-4ce7-9f2a-1e9f0b5741a4", "example": false, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": null, "tool_call_chunks": []}, "metadata": {"langfuse_session_id": "132322312213344", "langfuse_user_id": "21321312323444", "langfuse_tags": ["chat", "fastapi", "agent", "calculator"], "thread_id": "132322312213344", "user_id": "21321312323444", "langgraph_step": 3, "langgraph_node": "agent", "langgraph_triggers": ["branch:to:agent"], "langgraph_path": ["__pregel_pull", "agent"], "langgraph_checkpoint_ns": "agent:63c327a0-f51a-6a2e-68ff-4a3b86f48d99", "checkpoint_ns": "agent:63c327a0-f51a-6a2e-68ff-4a3b86f48d99", "ls_provider": "openai", "ls_model_name": "gpt://b1gbknonr2fm4ss0se7a/yandexgpt", "ls_model_type": "chat", "ls_temperature": null}}
    {"message": {"content": " old and new.", "additional_kwargs": {}, "response_metadata": {"finish_reason": "stop", "model_name": "gpt://b1gbknonr2fm4ss0se7a/yandexgpt"}, "type": "AIMessageChunk", "name": null, "id": "run--ad573982-3ca5-4ce7-9f2a-1e9f0b5741a4", "example": false, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": null, "tool_call_chunks": []}, "metadata": {"langfuse_session_id": "132322312213344", "langfuse_user_id": "21321312323444", "langfuse_tags": ["chat", "fastapi", "agent", "calculator"], "thread_id": "132322312213344", "user_id": "21321312323444", "langgraph_step": 3, "langgraph_node": "agent", "langgraph_triggers": ["branch:to:agent"], "langgraph_path": ["__pregel_pull", "agent"], "langgraph_checkpoint_ns": "agent:63c327a0-f51a-6a2e-68ff-4a3b86f48d99", "checkpoint_ns": "agent:63c327a0-f51a-6a2e-68ff-4a3b86f48d99", "ls_provider": "openai", "ls_model_name": "gpt://b1gbknonr2fm4ss0se7a/yandexgpt", "ls_model_type": "chat", "ls_temperature": null}}
    ```
    """
    logger = app.state.logger
    await logger.info(f"Received chat message for agent {agent_name}: {request.message}")

    inputs = {
        "messages": HumanMessage(content=request.message),
    }
    config = {
        "configurable": {"thread_id": request.thread_id, "user_id": request.user_id},
        "callbacks": [app.state.langfuse_callback_handler],
        "run_name": f"process-{agent_name}-chat-message",
        "metadata": {
            "langfuse_session_id": request.thread_id,
            "langfuse_user_id": request.user_id,
            "langfuse_tags": ["chat", "fastapi", "agent", agent_name],
        },
    }

    async def generate():
        # Get the agent dynamically based on agent_name
        agent = getattr(app.state, f"{agent_name}_agent")
        # Stream events from the agent call
        async for event in agent.astream(
            inputs,
            config=config,
            stream_mode="messages",
        ):
            await logger.debug(event)
            # Serialize the event
            message_obj = event[0]
            metadata = event[1]
            message_dict = message_obj.dict() if hasattr(message_obj, "dict") else str(message_obj)
            # Yield as newline-delimited JSON
            yield json.dumps({"message": message_dict, "metadata": metadata}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
