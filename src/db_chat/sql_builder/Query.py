""" Query Class """

from __future__ import annotations
import dataclasses


from enum import Enum
from typing import Annotated, List

from pydantic import BaseModel, Field



class SortOrder(BaseModel):
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


class Filter(BaseModel):
    """
    class to represent a filter
    """

    field: str
    operator: FilterOperator
    value: str|int|float|List[str|int|float]|any


class Functions(str, Enum):
    """
    class representing Filter operator
    """

    SUM = "SUM"
    MIN = "MIN"
    MAX = "MAX"
    AVG = "AVG"
    COUNT = "COUNT"
    CURRENT_DATE = "CURRENT_DATE"



class Expression(BaseModel):
    """
    Class to encapsulate a complex field
    """

    func: Annotated[ str, Field(description ="Optional. The aggregated function to be applied to the field")]
    parameters: List[Annotated[str,Field(description="List of params to the aggregate function. It can be fields or constants")]] = dataclasses.field(default_factory=lambda: [])
    alias: Annotated[str, Field(description=" Label or alias for the select column in query")] = None



class Join(BaseModel):
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


class Query(BaseModel):
    """
    Class to encapsulate the SQL query
    """

    table: Annotated[str,Field(description= "The name of the table. The table should be from the schema only")]
    fields: Annotated[List[ Annotated[str,Field(description="The select field name. In case of joined field use join alias followed by dot notation and then field name of joined column")] |
                 Annotated[ Expression,Field(description=" Expression in case of an aggregate function on a field")]], Field(description="List of fields . string in case of direct fields. If a aggregate funtion, use an expression object with func, list of parameters and alias name")] = dataclasses.field(default_factory=lambda: [])
    filters: list[Annotated[Filter,Field(description="List of filters to apply")]] = dataclasses.field(default_factory=lambda: [])
    group_by:Annotated[ list[str], Field(description=" The list of columns in the fields select to group by")] = dataclasses.field(default_factory=lambda: [])
    sort: Annotated[SortOrder,Field(description=" Sort field name and sort direction")] = None
    limit: Annotated[int,Field(description="No:of records to limit")]  = None
    offset: Annotated[int,Field(description="No:of records to skip/ offset")] = None
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
