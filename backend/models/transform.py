"""Models for data transformation configurations."""

from __future__ import annotations

from pydantic import BaseModel


class TransformConfig(BaseModel):
    """
    Represents configuration for data transformation steps.

    Attributes:
        identity_keys: List of attribute names or parsing paths that represent a unique entity.
        aggregate_keys: List of attribute names or parsing paths for aggregated unique entities.
        versioning_field: Field which represents version of entity.

    """

    identity_keys: list[str]
    aggregate_keys: list[str]
    versioning_field: str
