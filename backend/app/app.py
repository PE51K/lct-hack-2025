"""FastAPI application module for ETL generation, execution, and updates."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from core.logging import setup_logger
from core.settings import settings
from models.execute_etl import ExecuteETLRequest
from models.generate_etl import GenerateETLRequest
from models.update_etl import UpdateETLRequest

from .execute import execute_etl_endpoint
from .generate import generate_etl_endpoint
from .update import update_etl_endpoint

# ================== Setting up FastAPI ===================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events.
    """
    # Setup logging
    app.state.logger = await setup_logger(__name__)

    # Finalize startup
    yield

    # Shutdown logging
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

# ================== ETL Generation ===================

@app.post("/generate_etl")
async def generate_etl(request: GenerateETLRequest) -> StreamingResponse:
    """
    Generate ETL pipeline and recommendations based on input data URI.

    Args:
        request (GenerateETLRequest): The request containing input data URI and metadata.

    Returns:
        StreamingResponse: A streaming response with generation status updates.
    """
    return generate_etl_endpoint(request)

# ================== ETL Execution ===================

@app.post("/execute_etl")
async def execute_etl(request: ExecuteETLRequest) -> StreamingResponse:
    """
    Executes the ETL pipeline with provided metadata.

    Args:
        request (ExecuteETLRequest): The request containing metadata.

    Returns:
        StreamingResponse: A streaming response with execution status updates.
    """
    return execute_etl_endpoint(request)

# ================== ETL Update based on Feedback or Error ===================

@app.post("/update_etl")
async def update_etl(request: UpdateETLRequest) -> StreamingResponse:
    """
    Updates the ETL pipeline based on feedback or error messages.

    Args:
        request (UpdateETLRequest): The request containing feedback and metadata.

    Returns:
        StreamingResponse: A streaming response with update status.
    """
    return update_etl_endpoint(request)
