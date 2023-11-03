from __future__ import annotations
from db_chat.sql_builder.Filter import Filter
from db_chat.sql_builder.FilterOperator import FilterOperator
from db_chat.sql_builder.Query import Query, Expression, Functions

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


def test_simple():
    """
    Simple query
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
    assert Sql == "SELECT users.name, users.email \nFROM users"


def test_simple_join():
    """
    Simple join
    """

    query = Query(
        table="posts",
        fields=["title", "body", "user_name"],
    )

    Sql = builder.build_query(query=query)
    assert (
        Sql
        == "SELECT posts.title, posts.body, posts_post_user.name AS user_name \nFROM posts JOIN users AS posts_post_user ON posts.user_id = posts_post_user.id"
    )


def test_join_with_multiple_fields():
    """
    simple join with multiple fields
    """

    query = Query(
        table="posts",
        fields=["title", "body", "user_name", "user_email"],
    )
    S = builder.build_query(query=query)
    assert (
        S
        == "SELECT posts.title, posts.body, posts_post_user.name AS user_name, posts_post_user.email AS user_email \nFROM posts JOIN users AS posts_post_user ON posts.user_id = posts_post_user.id"
    )


def test_two_level_join():
    """
    Two level join
    """

    query = Query(
        table="comments",
        fields=["body", "comment_user_name"],
        filters=[],
        sort=["title"],
        limit=10,
        offset=10,
    )

    Sql = builder.build_query(query=query)
    assert (
        Sql
        == "SELECT comments.body, comments_post_comments_post_user.name AS comment_user_name \nFROM comments JOIN posts AS comments_post_comments ON comments.post_id = comments_post_comments.id JOIN users AS comments_post_comments_post_user ON comments_post_comments.user_id = comments_post_comments_post_user.id"
    )


def test_simple_filter():
    """
    Simple filter
    """
    query = Query(
        table="users",
        fields=["name", "email"],
        filters=[Filter(field="name", operator=FilterOperator.eq, value="John")],
        sort=["name"],
        limit=10,
        offset=10,
    )
    sql = builder.build_query(query=query)
    assert sql == "SELECT users.name, users.email \nFROM users \nWHERE users.name = :name_1"


# filters with joins
def test_filter_with_join():
    """
    Filter with join
    """
    query = Query(
        table="posts",
        fields=["title", "body", "user_name"],
        filters=[Filter(field="user_name", operator=FilterOperator.eq, value="John")],
    )
    sql = builder.build_query(query=query)
    assert (
        sql
        == "SELECT posts.title, posts.body, posts_post_user.name AS user_name \nFROM posts JOIN users AS posts_post_user ON posts.user_id = posts_post_user.id \nWHERE posts_post_user.name = :name_1"
    )


# aggregates and functions
def test_simple_aggregate():
    """
    Simple aggregate
    """
    query = Query(
        table="posts",
        fields=[Expression(func="SUM", params=["likes"], label="total_likes")],
        filters=[],
        sort=["title"],
        limit=10,
        offset=10,
    )
    sql = builder.build_query(query=query)
    assert sql == "SELECT sum(posts.likes) AS total_likes \nFROM posts"


def test_aggregate_with_columns():
    """
    Aggregate with columns
    """
    query = Query(
        table="posts",
        fields=[Expression(func="SUM", params=["likes"], label="total_likes"), "title"],
        filters=[],
        sort=["title"],
        limit=10,
        offset=10,
    )
    sql = builder.build_query(query=query)
    assert sql == "SELECT sum(posts.likes) AS total_likes, posts.title \nFROM posts GROUP BY posts.title"


# filters with aggregates and functions
def test_filters_with_aggregates():
    """
    Filters with aggregates
    """
    query = Query(
        table="posts",
        fields=["title"],
        filters=[Filter(Expression(func="SUM", params=["likes"]), operator=FilterOperator.eq, value=10)],
        sort=["title"],
        limit=10,
        offset=10,
    )
    sql = builder.build_query(query=query)
    assert sql == "SELECT posts.title \nFROM posts GROUP BY posts.title \nHAVING sum(posts.likes) = :sum_1"


# filters with constants and functions


# group by
def test_group_by():
    """
    Group by
    """
    query = Query(
        table="posts",
        fields=["title", "body", "user_name"],
        group_by=["title", "body", "user_name"],
    )
    sql = builder.build_query(query=query)
    assert (
        sql
        == "SELECT posts.title, posts.body, posts_post_user.name AS user_name \nFROM posts JOIN users AS posts_post_user ON posts.user_id = posts_post_user.id GROUP BY posts.title, posts.body, posts_post_user.name"
    )


# Having clause

# or and not and and conditions in joins
