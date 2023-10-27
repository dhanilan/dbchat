from db_chat.sql_builder.FilterOperator import FilterOperator


import dataclasses


@dataclasses.dataclass
class Filter:
    """
    class to represent a filter
    """

    field: str
    operator: FilterOperator
    value: str
