"""     Query Builder that builds SQL Alchmey Query """

from __future__ import annotations
from dataclasses import dataclass
from sqlalchemy import select, table, column

from db_chat.sql_builder.Query import Query
from db_chat.sql_builder.mappings import Relationship


@dataclass
class Schema:
    """
    Schema
    """

    tables: dict[str, Table]
    relationships: list[Relationship]


@dataclass
class Table:
    """
    Table
    """

    friendly_name: str
    name: str
    columns: dict[str, Column]
    relationships: list[str]


@dataclass
class Column:
    """
    Column
    """

    friendly_name: str
    name: str
    relationships: list[str]


class SQLAlchemyQueryBuilder:
    """
    Query Builder that builds SQL Alchmey Query
    """

    def __init__(self, schema: Schema):
        self.schema = schema

    def build_query(self, query: Query):
        """
        Build out the sql
        """

        # select the columns
        statement = self._build_select_clause(query)

        # # Start with the SELECT part
        # sql = self._build_select_clause(table, fields)

        # # Resolve relationships (JOINs)
        # sql = self._build_joins_and_from_clause(table, fields, filters, sql)

        # # WHERE clause
        # sql = self._build_where_clause(filters, sql)

        # # ORDER BY clause
        # sql = self._build_order_by_clause(sort, sql)

        # # LIMIT clause
        # sql = self._build_limit_clause(limit, sql)

        # # OFFSET clause
        # sql = self._build_offset_clause(offset, sql)

        sql = str(statement.compile())
        print(sql)
        return sql

    def _build_select_clause(self, query: Query):
        """
        Build the SELECT clause
        """

        sa_table = self._get_table_from_mapping(query.table)
        select_fields = self._get_select_fields(query.fields)
        statement = select(*select_fields).select_from(sa_table)

        return statement

    def _get_table_from_mapping(self, table_name: str):
        """
        Get the table from the mapping
        """

        # get the table from the schema
        schema_table = self.schema.tables[table_name]

        # get the columns
        sa_columns = []
        schema_column: Column
        for schema_column in schema_table.columns:
            sa_column = column(schema_column.name)
            sa_columns.append(sa_column)

        sa_table = table(schema_table.name, *sa_columns)

        return sa_table

    def _get_select_fields(self, fields: list[str]):
        """
        Get the select fields
        """

        # get the columns
        sa_columns = []
        field: str
        for field in fields:
            sa_column = column(field)
            sa_columns.append(sa_column)

        return sa_columns
