import dataclasses


@dataclasses.dataclass
class SortOrder:
    """
    Class to hold the sort direction and field
    """

    field: str
    direction: str
