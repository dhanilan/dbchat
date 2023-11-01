""" Query Class """
from __future__ import annotations
import dataclasses

from db_chat.sql_builder.Filter import Filter
from db_chat.sql_builder.SortOrder import SortOrder


from enum import Enum


class Functions(str, Enum):
    """
    class representing Filter operator
    """

    SUM = "SUM"
    MIN = "MIN"
    MAX = "MAX"
    AVG = "AVG"
    CURRENT_DATE = "CURRENT_DATE"


@dataclasses.dataclass
class Expression:
    """
    Class to encapsulate a complex field
    """

    func: str
    params: list[str] = dataclasses.field(default_factory=lambda: [])
    label: str = None


@dataclasses.dataclass
class Query:
    """
    Class to encapsulate the SQL query
    """

    table: str
    fields: list[str | Expression] = dataclasses.field(default_factory=lambda: [])
    filters: list[Filter] = dataclasses.field(default_factory=lambda: [])
    group_by: list[str | Expression] = dataclasses.field(default_factory=lambda: [])
    sort: SortOrder = None
    limit: int = None
    offset: int = None
