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

        from_clause = self._build_from_clause(query)

        select_clause = self._build_select_clause(query)

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

        statement = select(*select_clause).select_from(from_clause)
        sql = str(statement.compile())
        print(sql)
        return sql

    def _build_from_clause(self, query: Query):
        """
        Build the FROM clause
        """

        sa_table = self._get_table_from_mapping(query.table)
        statement = sa_table

        query_field: str | ComplexField
        for query_field in query.fields:
            field_name: str = query_field
            if isinstance(query_field, ComplexField):
                field_name = query_field.name

            # find column from schema tables by matching field_name
            # field_column = self.schema.tables[query.table].columns[field_name]
            field_column = next(
                (c for c in self.schema.tables[query.table].columns if c.name == field_name),
                None,
            )

            current_table = self._get_table_from_mapping(query.table)
            current_table_name = query.table
            current_alias = query.table
            if field_column.relationships:
                target_table_name = ""
                for relationship_name in field_column.relationships:
                    relationship_object: Relationship = next(
                        (rel for rel in self.schema.relationships if rel.name == relationship_name), None
                    )
                    if relationship_object.table1 == current_table_name:
                        target_table_name = relationship_object.table2
                        join_to_table = self._get_table_from_mapping(table_name=target_table_name)
                        source_column = statement.columns[relationship_object.field1]
                        target_column = join_to_table.columns[relationship_object.field2]

                    elif relationship_object.table2 == current_table_name:
                        target_table_name = relationship_object.table1
                        join_to_table = self._get_table_from_mapping(table_name=target_table_name)
                        source_column = statement.columns[relationship_object.field2]
                        target_column = join_to_table.columns[relationship_object.field1]

                    else:
                        raise ValueError(f"Unknown table in relationship: {relationship_name}")

                    current_alias += "_" + relationship_object.name
                    join_to_alias = alias(join_to_table, current_alias)

                    join_condition = source_column == target_column
                    # relationship_object.field1 == relationship_object.field2
                    statement = statement.join(join_to_alias, join_condition)

                    current_table = join_to_alias

        return statement

    def _build_select_clause(self, query: Query):
        """
        Build the SELECT clause
        """

        # get the columns
        sa_columns = []
        field_name: str | ComplexField
        for field in query.fields:
            field_name = field
            if isinstance(field, ComplexField):
                field_name = field.name
            field_column = next(
                (c for c in self.schema.tables[query.table].columns if c.name == field_name),
                None,
            )

            if field_column.relationships and len(field_column.relationships) > 0:
                aliased_table_name = query.table
                for relationship_name in field_column.relationships:
                    relationship_object: Relationship = next(
                        (rel for rel in self.schema.relationships if rel.name == relationship_name), None
                    )
                    aliased_table_name += "_" + relationship_object.name
                field_name = aliased_table_name + "." + field_name

            sa_column = column(field_name)
            sa_columns.append(sa_column)

        return sa_columns

        # sa_table = self._get_table_from_mapping(query.table)
        # select_fields = self._get_select_fields(query.fields)
        # statement = select(*select_fields).select_from(sa_table)

        # return statement

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
