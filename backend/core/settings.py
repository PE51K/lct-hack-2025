"""
Application settings for the Calculator API application.

Uses Pydantic's BaseSettings to manage configuration and environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

# ============ FastAPI backend app ============


class AppLoggingSettings(BaseSettings):
    """
    Settings for application logging.

    Attributes:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore",
    )

    log_level: str = "INFO"


class AppCORSSettings(BaseSettings):
    """
    Settings for FastAPI application CORS configuration.

    Attributes:
        origins (list[str]): List of allowed CORS origins.
        allow_credentials (bool): Whether to allow credentials in CORS.
        allow_methods (list[str]): List of allowed HTTP methods for CORS.
        allow_headers (list[str]): List of allowed HTTP headers for CORS.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_CORS_",
        extra="ignore",
    )

    origins: list[str]
    allow_credentials: bool
    allow_methods: list[str]
    allow_headers: list[str]


class AppSettings(BaseSettings):
    """
    Settings for FastAPI application.

    Attributes:
        logging (AppLoggingSettings): Logging configuration settings.
        cors (AppCORSSettings): CORS configuration settings.
    """

    logging: AppLoggingSettings = AppLoggingSettings()
    cors: AppCORSSettings = AppCORSSettings()


# ============ AI-related integrations ============


class YandexGPTSettings(BaseSettings):
    """
    Settings for Yandex GPT API integration.

    Attributes:
        api_key (str): API key for Yandex GPT.
        base_url (str): Base URL for Yandex GPT API.
        folder_id (str): Folder ID for Yandex GPT.
        model (str): Model name for Yandex GPT.
        model_version (str): Model version for Yandex GPT (default: "latest").
        model_name (str): Constructed model name in format gpt://{folder_id}/{
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="YANDEX_GPT_",
        extra="ignore",
    )

    api_key: str
    base_url: str
    folder_id: str
    model: str
    model_version: str

    @property
    def model_name(self) -> str:
        """
        Get the model name for Yandex GPT in format of gpt://{folder_id}/{model}.

        Returns:
            str: The model name for Yandex GPT.
        """
        return f"gpt://{self.folder_id}/{self.model}"


class AISettings(BaseSettings):
    """
    Settings for AI-related configurations.

    Attributes:
        yandex_gpt (YandexGPTSettings): Settings for Yandex GPT integration.
        langgraph_checkpointer (LanggraphCheckpointerPostgresSettings):
            Settings for Langgraph Checkpointer PostgreSQL connection.
    """

    yandex_gpt: YandexGPTSettings = YandexGPTSettings()


# ============ Main Settings Aggregator ============


class Settings(BaseSettings):
    """
    Main settings class that holds all application settings.

    Attributes:
        app (AppSettings): Instance of AppSettings containing application server settings.
        ai (AISettings): Instance of AISettings containing AI-related settings.
    """

    app: AppSettings = AppSettings()
    ai: AISettings = AISettings()


# Singleton instance of Settings
settings = Settings()


__all__ = ["settings"]
