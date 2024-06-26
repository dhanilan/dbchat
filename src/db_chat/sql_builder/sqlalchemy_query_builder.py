"""     Query Builder that builds SQL Alchmey Query """

from __future__ import annotations

from pydantic import BaseModel

from db_chat.sql_builder.schema import Column, Schema, Table
from sqlalchemy import Label, alias, and_, select, table, column, TableClause, func, ColumnClause
from db_chat.sql_builder.Filter import Filter
from db_chat.sql_builder.FilterOperator import FilterOperator

from db_chat.sql_builder.Query import Expression, Functions, Query
from db_chat.sql_builder.mappings import Relationship


class ValidationError(BaseModel):
    message: str



class SQLAlchemyQueryBuilder:
    """
    Query Builder that builds SQL Alchmey Query
    """

    query: Query
    sa_table: TableClause
    joined_paths: list[str] = []
    joined_tables: dict[str] = {}
    labeled_columns: dict[str] = {}
    select_columns: list = []

    def __init__(self, schema: Schema):
        self.schema = schema

    def validate(self,query:Query):
        """
        Validate the query
        """

        validation_errors:list[ValidationError] = []
        if query.table not in self.schema.tables:
            validation_errors.append(ValidationError(message= f"Table {query.table} not found in schema"))

        for join_key in query.joins:
            join = query.joins[join_key]
            if join.table not in self.schema.tables:
                validation_errors.append(ValidationError(message= f"Table {join.table} not found in schema"))

        for filter_obj in query.filters:
            if not self._is_expression(filter_obj.field):
                if not self._is_field_of_table(filter_obj.field, query.table):
                    validation_errors.append(ValidationError(message= f"Field {filter_obj.field} not found in table {query.table}"))

        for group_by_field in query.group_by:
            validation_errors.extend( self.validate_field(group_by_field, query))

        for field in query.fields:
            if self._is_expression(field):
                for param in field.parameters:
                    if not self._is_expression(param):
                        validation_errors.extend( self.validate_field(param, query))

                field.func = field.func.upper()
                if field.func not in [func.value for func in Functions]:
                    validation_errors.append(ValidationError(message= f"Invalid function {field.func}"))
            else:
                validation_errors.extend(self.validate_field(field, query))

        return validation_errors

    def validate_field(self, field:str,query:Query):
        """
        Validate the field
        """
        validation_errors:list[ValidationError] = []
        if not self._is_expression(field):

            if "." in field:
                # check if the field is a joined field
                join_key, field_name = field.split(".")
                join_table = query.joins.get(join_key)



                if join_table is None and join_key != query.table:
                    validation_errors.append(ValidationError(message= f"Join {join_key} not found in query"))
                elif join_key == query.table:
                    if not self._is_field_of_table(field_name, query.table):
                        validation_errors.append(ValidationError(message= f"Field {field_name} not found in table {query.table}"))
                elif not self._is_field_of_table(field_name, join_table.table):
                    validation_errors.append(ValidationError(message= f"Field {field_name} not found in table {join_table.table}"))

            elif not self._is_field_of_table(field, query.table):
                validation_errors.append(ValidationError(message= f"Field {field} not found in table {query.table}"))
        return validation_errors

    def build_query(self, query: Query):
        """
        Build out the sql
        """

        self.query = query
        self.sa_table = self._get_table_from_mapping(query.table)
        self.joined_paths = []
        self.joined_tables = {}
        self.select_columns = []

        statement = self._build_from_clause()

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

        if query.offset is not None:
            statement = statement.offset(query.offset)

        if query.limit is not None:
            statement = statement.limit(query.limit)


        sql = str(statement.compile(compile_kwargs={"literal_binds": True}))
        print(sql)
        return sql

    def _build_from_clause(self):
        """
        Build the FROM clause
        """

        self._build_joins()

        from_clause = self._build_select_clause_for_fields()

        from_clause, filter_clauses, sa_having_clauses = self._build_filter_clause(
            self.query, self.sa_table, self.joined_paths, self.joined_tables, from_clause
        )

        from_clause, group_by_clauses = self._build_group_by_columns(
            self.query, self.sa_table, self.joined_paths, self.joined_tables, from_clause, self.select_columns
        )

        self._append_non_having_clauses_to_group_by(self.select_columns, sa_having_clauses, group_by_clauses)

        statement = select(*self.select_columns).select_from(from_clause)

        if len(filter_clauses) > 0:
            statement = statement.where(and_(*filter_clauses))

        if len(group_by_clauses) > 0:
            statement = statement.group_by(*group_by_clauses)

        if sa_having_clauses and len(sa_having_clauses) > 0:
            statement = statement.having(and_(*sa_having_clauses))

        if self.query.sort is not None:
            sort_column = self._build_order_by_clause(self.query, self.sa_table, self.joined_paths, self.joined_tables, from_clause, self.select_columns,statement)
            statement = statement.order_by(sort_column.desc() if self.query.sort.direction == "desc" else sort_column.asc())

        return statement

    def _build_joins(self):
        for join_key in self.query.joins:
            join = self.query.joins[join_key]
            join_table = self._get_table_from_mapping(join.table)
            join_to_aliased_table = alias(join_table, join_key)
            join_condition = self.sa_table.columns.get(join.field) == join_to_aliased_table.columns.get(
                join.related_field
            )
            self.sa_table = self.sa_table.join(join_to_aliased_table, join_condition)
            self.joined_paths.append(join_key)
            self.joined_tables[join_key] = join_to_aliased_table

    def _append_non_having_clauses_to_group_by(self, select_columns, sa_having_clauses, group_by_clauses):
        select_columns_without_aggregates = [
            select_column for select_column in select_columns if not self._is_sa_column_aggregate(select_column)
        ]
        if sa_having_clauses and len(sa_having_clauses) > 0:
            group_by_clauses += select_columns_without_aggregates

    def _build_group_by_columns(
        self, query: Query, sa_table: TableClause, joined_paths, joined_tables, from_clause, select_columns
    ):
        group_by_columns = []
        if query.group_by is None:
            group_by_columns = []
        for group_by_field in query.group_by:
            group_by_column = self._get_field_from_table(query.table, group_by_field)

            if isinstance(group_by_column, ColumnClause):
                group_by_columns.append(group_by_column)
                continue
            if isinstance(group_by_column,Column):
                for column in sa_table.columns:
                    if column.name == group_by_column.name:
                        sa_grouping_column = column
                        continue
                #
            else:
                from_clause, join_to_aliased_table = self._build_join_for_relationship(
                    sa_table, from_clause, joined_paths, joined_tables, group_by_column, query.table, query.table
                )
                sa_grouping_column = join_to_aliased_table.columns.get(group_by_column.related_field)

            group_by_columns.append(sa_grouping_column)

        # if the list of field has aggregation functions then add all the fields to the group by
        has_aggregates = any(self._is_sa_column_aggregate(select_column) for select_column in select_columns)

        if has_aggregates:
            for select_column in [
                select_column for select_column in select_columns if not self._is_sa_column_aggregate(select_column)
            ]:
                group_by_columns.append(select_column)

        return from_clause, group_by_columns

    def _build_order_by_clause(self, query: Query, sa_table: TableClause, joined_paths, joined_tables, from_clause, select_columns,statement):
        """
        Build the ORDER BY clause
        """

        if query.sort is None:
            return None

        sort_column = self._get_field_from_table(query.table, query.sort.field)

        if isinstance(sort_column, ColumnClause):
            return sort_column

        if isinstance(sort_column,Column):
            sa_sort_column = sa_table.columns.get(sort_column.name)
            return sa_sort_column
        else:
            sort_column = self.labeled_columns[query.sort.field]
            if sort_column is not None:
                return sort_column

        raise ValueError(f"Field {query.sort.field} not found in table or its joined tables")


    def _is_sa_column_aggregate(self, select_column):
        return isinstance(select_column, Label) and isinstance(select_column.element, func.sum().__class__)

    def _is_condition_has_aggregate(self, filter_clause):
        if (
            isinstance(filter_clause.right, func.sum().__class__)
            or isinstance(filter_clause.right, func.avg().__class__)
            or isinstance(filter_clause.right, func.min().__class__)
            or isinstance(filter_clause.right, func.max().__class__)
        ):
            return True
        if (
            isinstance(filter_clause.left, func.sum().__class__)
            or isinstance(filter_clause.left, func.avg().__class__)
            or isinstance(filter_clause.left, func.min().__class__)
            or isinstance(filter_clause.left, func.max().__class__)
        ):
            return True
        return False

    def _build_filter_clause(self, query: Query, sa_table: TableClause, joined_paths, joined_tables, from_clause):
        sa_having_clauses = []

        filter_clauses = []
        for filter_obj in query.filters:
            if not self._is_expression(filter_obj.field):
                filter_column = self._get_field_from_table(query.table, filter_obj.field)

                if not filter_column.relationships:
                    sa_filter_column = sa_table.columns.get(filter_column.name)
                else:
                    from_clause, join_to_aliased_table = self._build_join_for_relationship(
                        sa_table, from_clause, joined_paths, joined_tables, filter_column, query.table, query.table
                    )
                    sa_filter_column = join_to_aliased_table.columns.get(filter_column.related_field)
                filter_clause = self._get_filter_condition_for_operator(filter_obj, sa_filter_column)

            else:
                sa_filter_column = self._build_clause_for_expression(
                    query, from_clause, filter_obj.field, sa_table, joined_paths, joined_tables
                )
                filter_clause = self._get_filter_condition_for_operator(filter_obj, sa_filter_column)
            if not self._is_condition_has_aggregate(filter_clause):
                filter_clauses.append(filter_clause)
            else:
                sa_having_clauses.append(filter_clause)

        return from_clause, filter_clauses, sa_having_clauses

    def _get_filter_condition_for_operator(self, filter_obj: Filter, sa_filter_column):
        # switch case for operators
        operator = filter_obj.operator.value

        filter_clause = {
            f"{FilterOperator.eq.value}": lambda x, y: x == y,
            f"{FilterOperator.neq.value}": lambda x, y: x != y,
            f"{FilterOperator.gt.value}": lambda x, y: x > y,
            f"{FilterOperator.gte.value}": lambda x, y: x >= y,
            f"{FilterOperator.lt.value}": lambda x, y: x < y,
            f"{FilterOperator.lte.value}": lambda x, y: x <= y,
            f"{FilterOperator.like.value}": lambda x, y: x.like(y),
            f"{FilterOperator.in_.value}": lambda x, y: x.in_(y),

        }.get(
            operator
        )(sa_filter_column, filter_obj.value)

        return filter_clause

    def _build_select_clause_for_fields(self):
        from_clause = self.sa_table
        query_field: str | Expression
        for query_field in self.query.fields:
            field_name: str = query_field
            if isinstance(query_field, Expression):
                sa_expression_function = self._build_clause_for_expression(
                    self.query, from_clause, query_field, self.sa_table, self.joined_paths, self.joined_tables
                )
                self.select_columns.append(sa_expression_function)
                continue

            field_column = self._get_field_from_table(self.query.table, field_name)

            current_table_name = self.query.table
            current_alias = self.query.table

            if isinstance(field_column, ColumnClause):
                self.select_columns.append(field_column)
                continue

            if not field_column.relationships:
                sa_colum_to_select = self._get_sa_column_from_sa_table_clause(
                    self.sa_table, field_column.name, self.query.table
                )
                self.select_columns.append(sa_colum_to_select)
                continue

            if field_column.relationships:
                from_clause, join_to_aliased_table = self._build_join_for_relationship(
                    self.sa_table,
                    from_clause,
                    self.joined_paths,
                    self.joined_tables,
                    field_column,
                    current_table_name,
                    current_alias,
                )

                self.select_columns.append(
                    join_to_aliased_table.columns.get(field_column.related_field).label(field_column.name)
                )
                continue

        return from_clause

    def _get_sa_column_from_sa_table_clause(self, sa_table: TableClause, column_name: str, sa_table_name: str):
        for column in sa_table.columns:
            if column.name == column_name and column.table.name == sa_table_name:
                return column
        return None

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

        for func_param in expression.parameters:
            if not self._is_expression(func_param):
                # if not a expression check if it is a field of the table
                is_field_of_table = self._is_field_of_table(func_param, query.table)
                if is_field_of_table:

                    field_column = self._get_field_from_table(query.table, func_param)

                    if isinstance(field_column, ColumnClause):
                        function_parms.append(field_column)
                        continue
                    if isinstance(field_column,Column):
                        for column in sa_table.columns:
                            if column.name == field_column.name:
                                function_parms.append(column)
                                continue
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

        sa_function = self._get_sa_function(expression.func, function_parms, expression.alias)

        return sa_function

    def _get_sa_function(self, func_name: str, function_parms: list, label: str):
        sa_function = None
        if func_name == Functions.SUM.value:
            sa_function = func.sum(*function_parms)

        if func_name == Functions.AVG.value:
            sa_function = func.avg(*function_parms)

        if func_name == Functions.COUNT.value:
            sa_function = func.count(*function_parms)
        if func_name == Functions.MAX.value:
            sa_function = func.max(*function_parms)

        if func_name == Functions.MIN.value:
            sa_function = func.min(*function_parms)



        if label:
            sa_function = sa_function.label(label)
            self.labeled_columns[label]  =  sa_function

        return sa_function

    def _is_expression(self, input_str: str|Expression):
        if type(input_str) == Expression or  type(input_str) == dict:
            return True
        else:
            return False

        if isinstance(input_str, Expression):
            return True
        if "(" in input_str:
            return True
        if ")" in input_str:
            return True
        if "," in input_str:
            return True

        return False

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

    def _get_field_from_table(self, table_name, field_name: str,skip_joined_tables=False):
        if "." in field_name and not skip_joined_tables:
            table_name, field_name = field_name.split(".")

            joined_table = self.joined_tables.get(table_name,None)
            if joined_table is not None:
                joined_field = joined_table.columns.get(field_name)
            elif table_name == self.query.table:
                return self._get_table_from_mapping(self.query.table).columns.get(field_name,None)
            else:
                raise ValueError(f"Field {field_name} not found in table {table_name}")
            return joined_field
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
