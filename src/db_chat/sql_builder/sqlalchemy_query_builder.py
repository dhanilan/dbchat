"""     Query Builder that builds SQL Alchmey Query """


from db_chat.sql_builder import Query


class SQLAlchemyQueryBuilder:
    """
    Query Builder that builds SQL Alchmey Query
    """

    def __init__(self, table_mapping, field_mappings, relationships):
        self.table_mapping = table_mapping
        self.field_mappings = field_mappings
        self.relationships = relationships

    def build_query(self, query: Query):
        """
        Build out the sql
        """
        table = query.table
        fields = query.fields
        filters = query.filters
        sort = query.sort
        limit = query.limit
        offset = query.offset

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

        # return sql
