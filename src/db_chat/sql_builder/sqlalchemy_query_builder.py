"""     Query Builder that builds SQL Alchmey Query """

from __future__ import annotations
from dataclasses import dataclass
import dataclasses
from sqlalchemy import alias, select, table, column

from db_chat.sql_builder.Query import ComplexField, Query
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
    columns: list[Column]
    relationships: list[str] = dataclasses.field(default_factory=lambda: [])


@dataclass
class Column:
    """
    Column
    """

    friendly_name: str
    name: str
    relationships: list[str] = dataclasses.field(default_factory=lambda: [])
    related_field: str = None


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

        statement = self._build_from_clause(query)

        # select_clause = self._build_select_clause(query)

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

    def _build_from_clause(self, query: Query):
        """
        Build the FROM clause
        """

        sa_table = self._get_table_from_mapping(query.table)
        select_columns = []
        from_clause = sa_table

        query_field: str | ComplexField
        for query_field in query.fields:
            field_name: str = query_field
            if isinstance(query_field, ComplexField):
                field_name = query_field.name

            field_column = self._get_field_from_table(query.table, field_name)

            current_table_name = query.table
            current_alias = query.table

            if not field_column.relationships:
                select_columns.append(sa_table.columns.get(field_column.name))

            if field_column.relationships:
                for relationship_name in field_column.relationships:
                    relationship_object: Relationship = self._get_relationship_by_name(relationship_name)
                    if relationship_object.table1 == current_table_name:
                        join_to_table = self._get_table_from_mapping(table_name=relationship_object.table2)
                        source_column = from_clause.columns.get(relationship_object.field1)
                        target_field_name = relationship_object.field2

                    elif relationship_object.table2 == current_table_name:
                        target_table_name = relationship_object.table1
                        join_to_table = self._get_table_from_mapping(table_name=target_table_name)
                        source_column = from_clause.columns.get(relationship_object.field2)
                        target_field_name = relationship_object.field1

                    else:
                        raise ValueError(f"Unknown table in relationship: {relationship_name}")

                    current_alias += "_" + relationship_object.name
                    join_to_alias = alias(join_to_table, current_alias)
                    target_column = join_to_alias.columns.get(target_field_name)

                    join_condition = source_column == target_column
                    from_clause = from_clause.join(join_to_alias, join_condition)
                    select_columns.append(
                        join_to_alias.columns.get(field_column.related_field).label(field_column.name)
                    )

        statement = select(*select_columns).select_from(from_clause)

        return statement

    def _get_relationship_by_name(self, relationship_name):
        return next((rel for rel in self.schema.relationships if rel.name == relationship_name), None)

    def _get_field_from_table(self, table_name, field_name):
        return next(
            (c for c in self.schema.tables[table_name].columns if c.name == field_name),
            None,
        )

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
