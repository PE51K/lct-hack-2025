"""FastAPI application module for ETL generation, execution, and updates."""

import logging

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.logging import setup_logger
from core.settings import settings

from .routers import create_router, publish_router, update_router

logger = logging.getLogger(__name__)

# Configure standard logging level
logging.basicConfig(level=getattr(logging, settings.app.logging.log_level.upper()))


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

# Include routers
app.include_router(create_router)
app.include_router(publish_router)
app.include_router(update_router)
