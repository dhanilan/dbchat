"""     Query Builder that builds SQL Alchmey Query """

from __future__ import annotations

from dataclasses import dataclass
import dataclasses

from sqlalchemy import MetaData, create_engine

from db_chat.sql_builder.Query import Expression, Query


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


@dataclass
class Column:
    """
    Column
    """

    friendly_name: str
    name: str
    relationships: list[str] = dataclasses.field(default_factory=lambda: [])
    related_field: str|None = None


@dataclasses.dataclass
class Relationship:
    """
    Class to hold a relationship between two tables
    """

    name: str
    table1: str
    field1: str
    table2: str
    field2: str


def validate_schema(schema: Schema, query: Query) -> list[str]:
    messages = []

    # check the table
    if query.table not in schema.tables:
        messages.append(f"Table {query.table} not found in the schema")

    # check the fields
    for field in query.fields:
        if isinstance(field, Expression):
            continue
        if field not in [column.name for column in schema.tables[query.table].columns]:
            messages.append(f"Field {field} not found in the table {query.table}")

    # check the filters
    for filter in query.filters:
        if filter.field not in [column.name for column in schema.tables[query.table].columns]:
            messages.append(f"Field {filter.field} not found in the table {query.table} for filter")

    # check the sort
    if query.sort:
        if query.sort.field not in [column.name for column in schema.tables[query.table].columns]:
            messages.append(f"Field {query.sort.field} not found in the table {query.table} for sort")

    return messages


def build_schema(connection_string: str) -> Schema:
    """
    Build Schema from connection string
    """
    # Create an engine
    engine = create_engine(connection_string)

    # Create a MetaData instance
    metadata = MetaData()

    schema = Schema(tables={}, relationships=[])

    # Reflect the tables
    metadata.reflect(bind=engine)

    # Now you can access the Table objects using their names
    for table_name in metadata.tables:
        sa_table_object = metadata.tables[table_name]
        table = Table(friendly_name=table_name, name=table_name, columns=[])
        for sa_column in sa_table_object.columns:
            column = Column(
                friendly_name=sa_column.name,
                name=sa_column.name,
                relationships=[],
            )
            table.columns.append(column)
        schema.tables[table_name] = table

    for table_name in metadata.tables:
        sa_table_object = metadata.tables[table_name]
        for sa_foreign_key in sa_table_object.foreign_keys:
            sa_foreign_key.column.name
            sa_foreign_key_constraint = sa_foreign_key.constraint
            sa_foreign_key_columns = sa_foreign_key_constraint.columns
            relationship = Relationship(
                name=f"{sa_foreign_key_columns[0].table.name}_{sa_foreign_key.column.table.name}",
                table1=sa_foreign_key_columns[0].table.name,
                field1=sa_foreign_key_columns[0].name,
                table2=sa_foreign_key.column.table.name,
                field2=sa_foreign_key.column.name,
            )
            schema.relationships.append(relationship)

    table_columns = {}
    for table_name in schema.tables:
        table_columns[table_name] = [column for column in schema.tables[table_name].columns]

    # for relationship in schema.relationships:
    #     table1 = schema.tables[relationship.table1]
    #     table2 = schema.tables[relationship.table2]

    #     column: Column
    #     for column in table_columns[relationship.table1]:
    #         if column.name in [col.name for col in table2.columns]:
    #             column_name = f"{relationship.name}_{column.name}"
    #             friendly_name = f"{relationship.name}_{column.friendly_name}"
    #         else:
    #             column_name = column.name
    #             friendly_name = column.friendly_name
    #         new_column = Column(
    #             friendly_name=friendly_name,
    #             name=column_name,
    #             relationships=[relationship.name],
    #             related_field=column.name,
    #         )
    #         table2.columns.append(new_column)

    #     for column in table_columns[relationship.table2]:
    #         if column.name in [col.name for col in table1.columns]:
    #             column_name = f"{relationship.name}_{column.name}"
    #             friendly_name = f"{relationship.name}_{column.friendly_name}"
    #         else:
    #             column_name = column.name
    #             friendly_name = column.friendly_name

    #         new_column = Column(
    #             friendly_name=friendly_name,
    #             name=column_name,
    #             relationships=[relationship.name],
    #             related_field=column.name,
    #         )
    #         table1.columns.append(new_column)

    return schema
