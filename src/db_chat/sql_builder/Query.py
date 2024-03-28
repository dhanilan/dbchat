""" Query Class """

from __future__ import annotations
import dataclasses


from enum import Enum


@dataclasses.dataclass
class SortOrder:
    """
    Class to hold the sort direction and field
    """

    field: str
    direction: str


class FilterOperator(str, Enum):
    """
    class representing Filter operator
    """

    eq = "eq"
    neq = "neq"
    gt = "gt"
    lt = "lt"
    gte = "gte"
    lte = "lte"
    like = "like"
    in_ = "in"


@dataclasses.dataclass
class Filter:
    """
    class to represent a filter
    """

    field: any
    operator: FilterOperator
    value: str


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
class Join:
    """
    Class to encapsulate a join
    """

    # query: Query
    table: str

    # TODO: this should be a list of conditions rather than a single equality condition. But for later
    field: str = None
    related_field: str = None
    join_type: str = "JOIN"

    def __post_init__(self):
        if self.join_type not in ["JOIN", "LEFT JOIN", "RIGHT JOIN"]:
            raise ValueError("Invalid join type")


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
    joins: dict[str, Join] = dataclasses.field(default_factory=lambda: {})

    # def __init__(self, **kwargs):
    #     self.table = kwargs.get("table")
    #     self.fields = kwargs.get("fields")
    #     self.filters = [
    #         filter_obj if isinstance(filter_obj, Filter) else Filter(**filter_obj)
    #         for filter_obj in kwargs.get("filters", [])
    #     ]
    #     self.group_by = kwargs.get("group_by")
    #     if kwargs.get("sort"):
    #         self.sort = SortOrder(**kwargs.get("sort"))
    #     self.limit = kwargs.get("limit")
    #     self.offset = kwargs.get("offset")
