"""This is a Sample Python file."""
from __future__ import annotations
from db_chat.sql_builder.Filter import Filter
from db_chat.sql_builder.FilterOperator import FilterOperator
from db_chat.sql_builder.Query import Query
from db_chat.sql_builder.SortOrder import SortOrder

from db_chat.sql_builder.mappings import Relationship


def get_operator_sql(op_type: FilterOperator):
    """
    Get the operator
    """
    operators = {"eq": "=", "neq": "<>", "gt": ">", "lt": "<", "gte": ">=", "lte": "<=", "like": "like", "in": "in"}

    return operators.get(f"{op_type.value}", "")


# TODO: this is rubbish, fix it
def _get_filter_rhs(filter_obj: Filter):
    # TODO: Prevent sql injection
    if filter_obj.operator == FilterOperator.in_:
        val = ""
        # check if the value is a list of strings or a list of ints

        if isinstance(filter_obj.value, list):
            if len(filter_obj.value) > 0:
                if isinstance(filter_obj.value[0], str):
                    for v in filter_obj.value:
                        val += f"'{v}',"
                    val = val[:-1]
                    return f"({val})"

                elif isinstance(filter_obj.value[0], int):
                    for v in filter_obj.value:
                        val += f"{v},"
                    val = val[:-1]
                    return f"({val})"
                else:
                    for v in filter_obj.value:
                        val += f"'{str(v)}',"
                    val = val[:-1]
                    return f"({val})"
            else:
                return f"({val})"

        return f"({val})"
    if filter_obj.operator == FilterOperator.like:
        return f"'%{filter_obj.value}%'"
    else:
        return f"'{filter_obj.value}'"


class SQLBuilder:
    """
    The SQL Builder which builds and emits the SQL
    """

    def __init__(self, table_mapping, field_mappings, relationships):
        self.table_mapping = table_mapping
        self.field_mappings = field_mappings
        self.relationships = relationships

    def build_sql(self, query: Query) -> str:
        """
        Build out the sql
        """
        table = query.table
        fields = query.fields
        filters = query.filters
        sort = query.sort
        limit = query.limit
        offset = query.offset

        # Start with the SELECT part
        sql = self._build_select_clause(table, fields)

        # Resolve relationships (JOINs)
        sql = self._build_joins_and_from_clause(table, fields, filters, sql)

        # WHERE clause
        sql = self._build_where_condition(table, filters, sql)

        # GROUP BY clause for aggregate fields
        sql = self._build_group_by(table, fields, sql)

        # HAVING clause for aggregate filters
        sql = self._build_having(table, filters, sql)

        # Sort order
        if sort:
            sql += self._build_sort_order(table, sort)

        # Offset
        if offset:
            sql += f" OFFSET {offset}"

        # Limit
        if limit:
            sql += f" LIMIT {limit}"

        return sql

    def _build_select_clause(self, root_table, fields):
        select_fields = []
        for field in fields:
            select_field = self._resolve_field_name_for_select(root_table, field)
            select_fields.append(select_field)

        sql = f"SELECT {', '.join(select_fields)} FROM {self.table_mapping[root_table]}"
        return sql

    def _resolve_field_name_for_select(self, root_table: str, field: str) -> str:
        field_detail = self.field_mappings[root_table].get(field, None)
        if not field_detail:
            raise ValueError(f"Unknown field: {field}")

        if isinstance(field_detail, dict) and "relationships" in field_detail and "aggregate" not in field_detail:
            # get last table in the relationship
            alias = field_detail["relationships"][-1]
            return f"{alias}.{field_detail['field']}"
        # TODO: handle aggregate fields in join tables, usually it doesn't make sense to have agg fields in join tables
        elif isinstance(field_detail, dict) and "aggregate" in field_detail:
            return self._add_aggregate_field(root_table, field, field_detail)

        else:
            return f"{self.table_mapping[root_table]}.{field_detail} AS {field}"

    def _add_aggregate_field(self, root_table, field, field_detail):
        agg_function = field_detail["aggregate"]

        if agg_function == "listagg":
            return f"listagg(DISTINCT {field_detail['field']}, ',') AS {field}"

        return f"{agg_function}({self.table_mapping[root_table]}.{field_detail['field']}) AS {field}"

    def _build_joins_and_from_clause(self, root_table, fields, filters: list[Filter], sql):
        mappings = self.field_mappings[root_table]
        all_relationships = []

        all_fields = fields + [filter.field for filter in filters]

        for field in all_fields:
            mapping = mappings.get(field, {})
            if isinstance(mapping, dict) and "relationships" in mapping:
                all_relationships.append(mapping["relationships"])

        added_joins = set()
        for relationship_objs in all_relationships:
            prev_relationship = None
            relationship_name: str
            for relationship_name in relationship_objs:
                if relationship_name not in added_joins:
                    rel: Relationship
                    for rel in self.relationships:
                        if rel.name == relationship_name:
                            join_from = prev_relationship if prev_relationship else self.table_mapping[rel.table1]
                            sql += f" JOIN {self.table_mapping[rel.table2]}  AS {rel.name}"
                            sql += f" ON {join_from}.{rel.field1} = {rel.name}.{rel.field2}"
                            added_joins.add(rel.name)
                prev_relationship = relationship_name

        return sql

    def _resolve_field_name(self, root_table: str, field: str) -> str:
        field_detail = self.field_mappings[root_table].get(field, None)
        if not field_detail:
            raise ValueError(f"Unknown field: {field}")

        if isinstance(field_detail, dict) and "relationships" in field_detail:
            # get last table in the relationship
            alias = field_detail["relationships"][-1]
            return f"{alias}.{field_detail['field']}"

        # TODO: handle aggregate fields in join tables, usually it doesn't make sense to have agg fields in join tables
        elif isinstance(field_detail, dict) and "aggregate" in field_detail:
            return f"{field_detail['field']}"

        else:
            return f"{self.table_mapping[root_table]}.{field_detail}"

    def _build_where_condition(self, root_table, filters, sql):
        where_conditions = []
        filter_obj: Filter
        for filter_obj in filters:
            if "aggregate" not in self.field_mappings[root_table][filter_obj.field]:
                field_name = self._resolve_field_name(root_table, filter_obj.field)
                operator = get_operator_sql(filter_obj.operator)
                field_value = _get_filter_rhs(filter_obj)
                where_conditions.append(f"{field_name} {operator} {field_value}")

        if where_conditions:
            sql += f" WHERE {' AND '.join(where_conditions)}"

        return sql

    def _build_having(self, root_table, filters: list[Filter], sql):
        having_conditions = []
        for filter_obj in filters:
            if "aggregate" in self.field_mappings[root_table][filter_obj.field]:
                having_conditions.append(
                    f"{filter_obj.field} {get_operator_sql(filter_obj.operator)} {_get_filter_rhs(filter_obj)}"
                )

        if having_conditions:
            sql += f" HAVING {' AND '.join(having_conditions)}"

        return sql

    def _build_group_by(self, root_table, fields, sql):
        group_fields = [f for f in fields if "aggregate" not in self.field_mappings[root_table][f]]
        if any("aggregate" in self.field_mappings[root_table][f] for f in fields):
            group_by_fields = [self._resolve_field_name(root_table, field) for field in group_fields]
            sql += f" GROUP BY {', '.join(group_by_fields)}" if any(group_by_fields) else ""
        return sql

    def _build_sort_order(self, root_table, sort: SortOrder):
        if sort is None or sort.field is None:
            return ""
        if self.field_mappings[root_table][sort.field]:
            sort_dir = sort.direction.value if hasattr(sort.direction, "value") else sort.direction
            return f" ORDER BY {sort.field} {sort_dir}"
        else:
            raise ValueError(f"Unknown field: {sort.field}")
