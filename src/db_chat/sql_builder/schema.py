"""     Query Builder that builds SQL Alchmey Query """

from __future__ import annotations

from dataclasses import dataclass
import dataclasses

from sqlalchemy import MetaData, create_engine


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
        table = Table(
            friendly_name=table_name,
            name=table_name,
            columns=[],
            relationships=[],
        )
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
                name=sa_foreign_key.name,
                table1=sa_foreign_key.column.table.name,
                field1=sa_foreign_key.column.name,
                table2=sa_foreign_key.column.table.name,
                field2=sa_foreign_key.column.name,
            )
            schema.relationships.append(relationship)
    return schema
