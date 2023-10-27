"""Module to represent schema """

from __future__ import annotations
import dataclasses


@dataclasses.dataclass
class Relationship:
    """
    Class to hold a relationship between two tables
    """

    name: str
    table1: str
    field1: str
    table2: str
    field2: str


@dataclasses.dataclass
class UserFriendlyMappings:
    """
    User friendly Names
    """

    fields: list[str]
    metrics: list[str]
    aggregate_metrics: list[str]
