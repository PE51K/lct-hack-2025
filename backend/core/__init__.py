"""
Core Module for Backend Application.

This module provides the fundamental building blocks and utilities used throughout
the backend application. It centralizes configuration management, logging setup,
and other core functionality to ensure consistency and maintainability.

Main Components:
- **Settings Management**: Centralized configuration using Pydantic BaseSettings
  for environment variables, API keys, and service configurations
- **Logging Utilities**: Asynchronous logging setup with structured formatting
  and proper log levels for different components

Key Features:
- ✅ **Environment-based Configuration**: Flexible settings that adapt to different
  deployment environments (development, staging, production)
- ✅ **Type-safe Settings**: Pydantic validation ensures configuration correctness
- ✅ **Async Logging**: Non-blocking logging suitable for high-performance applications
- ✅ **Modular Design**: Clean separation of concerns with focused responsibilities

Usage:
    ```python
    # Import core components
    from core.settings import settings
    from core.logging import setup_logger

    # Access application settings
    yandex_api_key = settings.ai.yandex_gpt.api_key

    # Set up logging
    logger = await setup_logger(__name__)
    await logger.info("Application started")
    ```

Configuration:
    The settings are automatically loaded from environment variables defined in
    the .env file. See .env.example for all available configuration options.

Dependencies:
    - pydantic: For settings validation and type safety
    - aiologger: For asynchronous logging capabilities
    - pydantic-settings: For environment variable integration

Note:
    This module serves as the foundation for the entire backend application.
    All other modules should import and use these core utilities for consistency.
"""
