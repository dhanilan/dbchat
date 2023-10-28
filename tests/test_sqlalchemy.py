from __future__ import annotations
from db_chat.sql_builder.Query import Query

from db_chat.sql_builder.sqlalchemy_query_builder import SQLAlchemyQueryBuilder, Schema

schema: Schema = Schema(
    tables={
        "users": {
            "friendly_name": "users",
            "name": "users",
            "columns": {
                "name": {"friendly_name": "name", "name": "name", "relationships": []},
                "id": {"friendly_name": "id", "name": "id", "relationships": []},
                "email": {"friendly_name": "email", "name": "email", "relationships": []},
            },
            "relationships": [],
        }
    },
    relationships=[],
)
builder = SQLAlchemyQueryBuilder(schema)


def test_simple():
    """
    This defines the expected usage, which can then be used in various test cases.
    Pytest will not execute this code directly, since the function does not contain the suffex "test"
    """

    query = Query(
        table="users",
        fields=["name", "email"],
        filters=[],
        sort=["name"],
        limit=10,
        offset=10,
    )

    builder.build_query(query=query)
