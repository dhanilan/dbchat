""" Query Class """
from __future__ import annotations
import dataclasses

from db_chat.sql_builder.Filter import Filter
from db_chat.sql_builder.SortOrder import SortOrder


@dataclasses.dataclass
class Query:
    """
    Class to encapsulate the SQL query
    """

    table: str
    fields: list[str]
    filters: list[Filter] = dataclasses.field(default_factory=lambda: [])
    sort: SortOrder = None
    limit: int = None
    offset: int = None
