from __future__ import annotations
from db_chat.sql_builder.Query import Query

from db_chat.sql_builder.sqlalchemy_query_builder import Column, SQLAlchemyQueryBuilder, Schema, Table


schema: Schema = Schema(
    tables={
        "users": Table(
            name="users",
            friendly_name="users",
            columns=[
                Column(name="name", friendly_name="name", relationships=[]),
                Column(name="id", friendly_name="id", relationships=[]),
                Column(name="email", friendly_name="email", relationships=[]),
            ],
            relationships=[],
        )
    },
    relationships=[],
)

print(schema.tables["users"].columns[0].name)
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

    Sql = builder.build_query(query=query)
    assert Sql == "SELECT name, email \nFROM users"
