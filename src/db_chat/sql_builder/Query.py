""" Query Class """
from __future__ import annotations
import dataclasses

from db_chat.sql_builder.Filter import Filter
from db_chat.sql_builder.SortOrder import SortOrder


@dataclasses.dataclass
class ComplexField:
    """
    Class to encapsulate a complex field
    """

    name: str
    func: str
    params: list[any]


@dataclasses.dataclass
class Query:
    """
    Class to encapsulate the SQL query
    """

    table: str
    fields: list[str | ComplexField] = dataclasses.field(default_factory=lambda: [])
    filters: list[Filter] = dataclasses.field(default_factory=lambda: [])
    sort: SortOrder = None
    limit: int = None
    offset: int = None
