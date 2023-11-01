"""     Query Builder that builds SQL Alchmey Query """

from __future__ import annotations
from dataclasses import dataclass
import dataclasses
from sqlalchemy import alias, and_, select, table, column, TableClause, func
from db_chat.sql_builder.Filter import Filter
from db_chat.sql_builder.FilterOperator import FilterOperator

from db_chat.sql_builder.Query import Expression, Functions, Query
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
        joined_paths = []
        joined_tables: dict = {}

        from_clause = self._build_select_clause_for_fields(query, sa_table, select_columns, joined_paths, joined_tables)

        from_clause, filter_clauses = self._build_filter_clause(
            query, sa_table, joined_paths, joined_tables, from_clause
        )

        from_clause, group_by_clauses = self._build_group_by_columns(
            query, sa_table, joined_paths, joined_tables, from_clause
        )

        statement = select(*select_columns).select_from(from_clause)

        if len(filter_clauses) > 0:
            statement = statement.where(and_(*filter_clauses))

        if len(group_by_clauses) > 0:
            statement = statement.group_by(*group_by_clauses)

        return statement

    def _build_group_by_columns(self, query: Query, sa_table: TableClause, joined_paths, joined_tables, from_clause):
        group_by_columns = []
        for group_by_field in query.group_by:
            group_by_column = self._get_field_from_table(query.table, group_by_field)

            if not group_by_column.relationships:
                sa_grouping_column = sa_table.columns.get(group_by_column.name)
            else:
                from_clause, join_to_aliased_table = self._build_join_for_relationship(
                    sa_table, from_clause, joined_paths, joined_tables, group_by_column, query.table, query.table
                )
                sa_grouping_column = join_to_aliased_table.columns.get(group_by_column.related_field)

            group_by_columns.append(sa_grouping_column)
        return from_clause, group_by_columns

    def _build_filter_clause(self, query: Query, sa_table: TableClause, joined_paths, joined_tables, from_clause):
        filter_clauses = []
        for filter_obj in query.filters:
            filter_column = self._get_field_from_table(query.table, filter_obj.field)

            if not filter_column.relationships:
                sa_filter_column = sa_table.columns.get(filter_column.name)
            else:
                from_clause, join_to_aliased_table = self._build_join_for_relationship(
                    sa_table, from_clause, joined_paths, joined_tables, filter_column, query.table, query.table
                )
                sa_filter_column = join_to_aliased_table.columns.get(filter_column.related_field)
            filter_clause = self._get_filter_condition_for_operator(filter_obj, sa_filter_column)
            filter_clauses.append(filter_clause)
        return from_clause, filter_clauses

    def _get_filter_condition_for_operator(self, filter_obj: Filter, sa_filter_column):
        # switch case for operators
        operator = filter_obj.operator.value

        filter_clause = {
            f"{FilterOperator.eq.value}": lambda x, y: x == y,
        }.get(
            operator
        )(sa_filter_column, filter_obj.value)

        return filter_clause

    def _build_select_clause_for_fields(
        self, query: Query, sa_table: TableClause, select_columns: list, joined_paths, joined_tables
    ):
        from_clause = sa_table
        query_field: str | Expression
        for query_field in query.fields:
            field_name: str = query_field
            if isinstance(query_field, Expression):
                sa_expression_function = self._build_clause_for_expression(
                    query, from_clause, query_field, sa_table, joined_paths, joined_tables
                )
                select_columns.append(sa_expression_function)
                continue

            field_column = self._get_field_from_table(query.table, field_name)

            current_table_name = query.table
            current_alias = query.table

            if not field_column.relationships:
                select_columns.append(sa_table.columns.get(field_column.name))

            if field_column.relationships:
                from_clause, join_to_aliased_table = self._build_join_for_relationship(
                    sa_table, from_clause, joined_paths, joined_tables, field_column, current_table_name, current_alias
                )

                select_columns.append(
                    join_to_aliased_table.columns.get(field_column.related_field).label(field_column.name)
                )

        return from_clause

    def _build_clause_for_expression(
        self,
        query: Query,
        from_clause: TableClause,
        expression: Expression,
        sa_table: TableClause,
        joined_paths,
        joined_tables,
    ):
        function_parms = []

        for func_param in expression.params:
            if not self._is_expression(func_param):
                # if not a expression check if it is a field of the table
                is_field_of_table = self._is_field_of_table(func_param, query.table)
                if is_field_of_table:
                    field_column = self._get_field_from_table(query.table, func_param)
                    if not field_column.relationships:
                        function_parms.append(sa_table.columns.get(field_column.name))
                    else:
                        from_clause, join_to_aliased_table = self._build_join_for_relationship(
                            sa_table,
                            from_clause,
                            joined_paths,
                            joined_tables,
                            field_column,
                            query.table,
                            query.table,
                        )

                        function_parms.append(
                            join_to_aliased_table.columns.get(field_column.related_field).label(field_column.name)
                        )
                else:
                    # if not a field of the table then it is a constant
                    function_parms.append(func_param)

        sa_function = self._get_sa_function(expression.func, function_parms, expression.label)

        return sa_function

    def _get_sa_function(self, func_name: str, function_parms: list, label: str):
        sa_function = None
        if func_name == Functions.SUM.value:
            sa_function = func.sum(*function_parms)

        if label:
            sa_function = sa_function.label(label)

        return sa_function

    def _is_expression(self, input_str: str):
        return not input_str.isalnum()

    def _is_field_of_table(self, input_str: str, table_name: str):
        if self._get_field_from_table(table_name, input_str) is not None:
            return True
        return False

    def _build_join_for_relationship(
        self,
        sa_table: TableClause,
        from_clause,
        joined_paths: list,
        joined_tables: dict,
        field_column,
        current_table_name,
        current_alias,
    ):
        previous_table = sa_table
        for relationship_name in field_column.relationships:
            relationship_object: Relationship = self._get_relationship_by_name(relationship_name)
            if relationship_object.table1 == current_table_name:
                target_table_name = relationship_object.table2
                source_field_name = relationship_object.field1
                target_field_name = relationship_object.field2

            elif relationship_object.table2 == current_table_name:
                target_table_name = relationship_object.table1
                source_field_name = relationship_object.field2
                target_field_name = relationship_object.field1

            else:
                raise ValueError(f"Unknown table in relationship: {relationship_name}")

            current_alias += "_" + relationship_object.name

            if current_alias not in joined_paths:
                join_to_table = self._get_table_from_mapping(table_name=target_table_name)
                source_join_column = previous_table.columns.get(source_field_name)
                join_to_aliased_table = alias(join_to_table, current_alias)
                target_join_column = join_to_aliased_table.columns.get(target_field_name)
                join_condition = source_join_column == target_join_column
                from_clause = from_clause.join(join_to_aliased_table, join_condition)
                joined_paths.append(current_alias)
                joined_tables[current_alias] = join_to_aliased_table
            else:
                join_to_aliased_table = joined_tables[current_alias]

            current_table_name = target_table_name
            previous_table = join_to_aliased_table
        return from_clause, join_to_aliased_table

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
