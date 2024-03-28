from __future__ import annotations
from db_chat.sql_builder.Filter import Filter
from db_chat.sql_builder.FilterOperator import FilterOperator
from db_chat.sql_builder.Query import Join, Query, Expression

from db_chat.sql_builder.sqlalchemy_query_builder import Column, SQLAlchemyQueryBuilder, Schema, Table
from db_chat.sql_builder.mappings import Relationship


schema: Schema = Schema(
    tables={
        "users": Table(
            name="users",
            friendly_name="users",
            columns=[
                Column(name="name", friendly_name="name"),
                Column(name="id", friendly_name="id"),
                Column(name="email", friendly_name="email"),
                Column(name="posts", friendly_name="posts", relationships=["post_user"]),
            ],
        ),
        "posts": Table(
            name="posts",
            friendly_name="posts",
            columns=[
                Column(name="id", friendly_name="id"),
                Column(name="user_id", friendly_name="user_id"),
                Column(name="title", friendly_name="title"),
                Column(name="body", friendly_name="body"),
                Column(name="likes", friendly_name="likes"),
                Column(name="user_name", friendly_name="user name", relationships=["post_user"], related_field="name"),
                Column(
                    name="user_email", friendly_name="user email", relationships=["post_user"], related_field="email"
                ),
            ],
        ),
        "comments": Table(
            name="comments",
            friendly_name="comments",
            columns=[
                Column(name="id", friendly_name="id"),
                Column(name="post_id", friendly_name="post_id"),
                Column(name="body", friendly_name="body"),
                Column(
                    name="comment_user_name",
                    friendly_name="user name",
                    relationships=["post_comments", "post_user"],
                    related_field="name",
                ),
            ],
        ),
    },
    relationships=[
        Relationship(name="post_user", table1="posts", field1="user_id", table2="users", field2="id"),
        Relationship(name="post_comments", table1="posts", field1="id", table2="comments", field2="post_id"),
    ],
)

builder = SQLAlchemyQueryBuilder(schema)


def test_simple_join():
    """
    Simple join
    """

    query = Query(
        table="posts",
        fields=["title", "body", "post_user.name"],
        joins={
            "post_user": Join(
                table="users",
                field="user_id",
                related_field="id",
            )
        },
    )

    Sql = builder.build_query(query=query)
    print(Sql)
    assert (
        Sql
        == "SELECT posts.title, posts.body, post_user.name \nFROM posts JOIN users AS post_user ON posts.user_id = post_user.id"
    )
