"""
Filter Class
"""
import dataclasses
from typing import List

from db_chat.sql_builder.FilterOperator import FilterOperator


@dataclasses.dataclass
class Filter:
    """
    class to represent a filter
    """

    field: any
    operator: FilterOperator
    value: str|int|float|List[str|int|float]
