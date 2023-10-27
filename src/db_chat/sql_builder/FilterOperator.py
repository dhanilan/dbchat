from enum import Enum


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
