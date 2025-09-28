"""Kafka extract configuration builder and message reader."""

import json
from datetime import datetime
import sys

from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord

from models.extract import Content, ContentType, Source

sys.path.insert(0, "..")

from core.logging import setup_logger
from .base import BaseExtractConfigBuilder


class KafkaMessageReader:
    """Service class for reading messages from Kafka topics."""

    def __init__(self, bootstrap_servers: str, topic_name: str, group_id: str | None = None):
        """Initialize KafkaMessageReader."""
        self.bootstrap_servers = bootstrap_servers
        self.topic_name = topic_name
        self.group_id = group_id
        self.consumer = None

    async def setup_logging(self):
        """Setup logging configuration."""
        self.logger = await setup_logger(__name__)

    async def connect(self) -> bool | None:
        """Connect to Kafka."""
        await self.setup_logging()
        try:
            self.consumer = KafkaConsumer(
                self.topic_name,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset="latest",
                enable_auto_commit=True,
                value_deserializer=self.deserialize_message,
            )
            await self.logger.info(f"Successfully connected to Kafka: {self.bootstrap_servers}")
            await self.logger.info(f"Subscribed to topic: {self.topic_name}")
            return True
        except Exception as e:
            await self.logger.error(f"Connection error: {e}")
            return False

    def deserialize_message(self, message: bytes) -> object:
        """Deserialize message."""
        if message is None:
            return None

        try:
            return json.loads(message.decode("utf-8"))
        except json.JSONDecodeError:
            return message.decode("utf-8")
        except Exception:
            return message

    def process_message(self, message: ConsumerRecord):
        """Process individual message."""
        timestamp = datetime.fromtimestamp(message.timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n[{timestamp}] Message from {message.topic}")
        print(f"Partition: {message.partition}, Offset: {message.offset}")
        print(f"Key: {message.key}")
        print(f"Data: {message.value}")
        print("-" * 50)

    async def start_consuming(self, max_messages: int | None = None):
        """Start consuming messages."""
        if not self.consumer:
            await self.connect()
            if not self.consumer:
                await self.logger.error("Consumer not initialized")
                return

        message_count = 0
        await self.logger.info("Starting message reading...")

        try:
            for message in self.consumer:
                self.process_message(message)
                message_count += 1

                if max_messages and message_count >= max_messages:
                    await self.logger.info(f"Reached limit of {max_messages} messages")
                    break

        except KeyboardInterrupt:
            await self.logger.info("Received interrupt signal")
        except Exception as e:
            await self.logger.error(f"Error reading: {e}")
        finally:
            await self.close()

    async def close(self):
        """Close connection."""
        if self.consumer:
            self.consumer.close()
            await self.logger.info("Connection closed")


class KafkaExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for Kafka source configurations.

    Extracts metadata from Kafka topics by sampling messages.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from Kafka source."""
        raise NotImplementedError("Metadata extraction not implemented for Kafka sources.")

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for Kafka source.

        Args:
            source: Kafka source configuration.

        Returns:
            ContentType.json for Kafka messages.
        """
        raise NotImplementedError("Content type extraction not implemented for Kafka sources.")

    @classmethod
    async def get_content_statistics(cls, source: Source) -> dict:
        """Retrieve statistics about the source content.

        Args:
            source: The source configuration.

        Returns:
            Dictionary containing content statistics with
            any additional information about the source.
        """
        raise NotImplementedError(
            "Content statistics extraction not implemented for Kafka sources."
        )
