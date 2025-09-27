"""Models for data transformation configurations."""

from __future__ import annotations

from pydantic import BaseModel


class TransformConfig(BaseModel):
    """
    Represents configuration for data transformation steps.
    
    Attributes:
        identity_keys: list of attribute name or parsing paths wich represent unique entity
        aggregate_keys: list of attribute name or parsing paths wich represent aggregated unique entity
        versioning_field: field which represents version of entity
    
    """

    identity_keys: list[str]
    aggregate_keys: list[str]
    versioning_field: str

