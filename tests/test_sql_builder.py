from db_chat.sql_builder.sql_builder import SQLBuilder, Filter, Relationship, SortOrder, SQLQuery, FilterOperator

# Sample Configuration for the Test Cases
table_mapping = {
    "distribution_metrics": "viewership_metrics_day_level",
    "channel": "DW_DIM.channel",
    "content_playout_metrics": "CONTENT_PLAYOUT_METRICS_VIEW",
    "content_playout": "DW_DIM.CONTENT_PLAYOUT",
    "delivery": "DW_DIM.DELIVERY",
    "CUSTOMER": "DW_DIM.CUSTOMER",
    "content": "DW_DIM.AMAGI_ASSET",
    "genre": "DW_DIM.GENRE",
    "genre_mappings": "DW_DIM.GENRE_MAPPINGS",
}

field_mappings = {
    "distribution_metrics": {
        "channel_id": "dim_channel_id",
        "channel_name": {"relationships": ["distribution_channel"], "field": "name"},
        "unique_viewers": "metric_unique_viewers",
        "viewership_minutes": "METRIC_VIEWERSHIP_MINUTES",
        "avg_viewership_minutes": {"aggregate": "SUM", "field": "METRIC_VIEWERSHIP_MINUTES"},
    },
    "channel": {"id": "id", "name": "name"},
    "content_playout_metrics": {
        "unique_viewers": "METRIC_UNIQUE_VIEWERS",
        "content_playout_id": "DIM_CONTENT_PLAYOUT_ID",
        "content_title": {
            "relationships": ["content_playout_metrics_content_playout", "content_playout_content"],
            "field": "title",
        },
        "content_name": {
            "relationships": ["content_playout_metrics_content_playout", "content_playout_content"],
            "field": "name",
        },
        "genre": {
            "aggregate": "listagg",
            "field": "genre.name",
            "relationships": [
                "content_playout_metrics_content_playout",
                "content_playout_content",
                "genre_mappings",
                "genre",
            ],
        },
    },
    "content_playout": {"ID": "ID", "DELIVERY_ID": "DELIVERY_ID", "CONTENT_SOURCE_ASSET_ID": "CONTENT_SOURCE_ASSET_ID"},
    "delivery": {"ID": "ID", "CHANNEL_ID": "CHANNEL_ID"},
    "CUSTOMER": {"AMGID": "AMGID", "NAME": "NAME", "CUSTOMER_TYPE": "CUSTOMER_TYPE"},
    "content": {"NAME": "NAME", "TITLE": "TITLE"},
    "genre": {"NAME": "NAME"},
    "genre_mappings": {},
}

relationships = [
    Relationship(
        name="distribution_channel",
        table1="distribution_metrics",
        field1="dim_channel_id",
        table2="channel",
        field2="id",
    ),
    Relationship(
        name="content_playout_metrics_content_playout",
        table1="content_playout_metrics",
        field1="DIM_CONTENT_PLAYOUT_ID",
        table2="content_playout",
        field2="ID",
    ),
    Relationship(
        name="content_playout_content",
        table1="content_playout",
        field1="CONTENT_SOURCE_ASSET_ID",
        table2="content",
        field2="ID",
    ),
    Relationship(
        name="genre_mappings", table1="content_playout_content", field1="id", table2="genre_mappings", field2="asset_id"
    ),
    Relationship(name="genre", table1="genre_mappings", field1="GENRE_ID", table2="genre", field2="ID"),
]

builder = SQLBuilder(table_mapping, field_mappings, relationships)


def test_simple_field_selection():
    query = {"table": "distribution_metrics", "fields": ["channel_id"]}

    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert sql == "SELECT viewership_metrics_day_level.dim_channel_id AS channel_id FROM viewership_metrics_day_level"


def test_get_channel_name():
    query = {"table": "distribution_metrics", "fields": ["channel_id", "channel_name"]}
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT viewership_metrics_day_level.dim_channel_id AS channel_id, distribution_channel.name FROM viewership_metrics_day_level JOIN DW_DIM.channel  AS distribution_channel ON viewership_metrics_day_level.dim_channel_id = distribution_channel.id"
    )


def test_aggregate_field_selection():
    query = {"table": "distribution_metrics", "fields": ["channel_id", "avg_viewership_minutes"]}
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT viewership_metrics_day_level.dim_channel_id AS channel_id, SUM(viewership_metrics_day_level.METRIC_VIEWERSHIP_MINUTES) AS avg_viewership_minutes FROM viewership_metrics_day_level GROUP BY viewership_metrics_day_level.dim_channel_id"
    )


def test_nested_join():
    query = {"table": "content_playout_metrics", "fields": ["unique_viewers", "content_title", "content_name"]}
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT CONTENT_PLAYOUT_METRICS_VIEW.METRIC_UNIQUE_VIEWERS AS unique_viewers, content_playout_content.title, content_playout_content.name FROM CONTENT_PLAYOUT_METRICS_VIEW JOIN DW_DIM.CONTENT_PLAYOUT  AS content_playout_metrics_content_playout ON CONTENT_PLAYOUT_METRICS_VIEW.DIM_CONTENT_PLAYOUT_ID = content_playout_metrics_content_playout.ID JOIN DW_DIM.AMAGI_ASSET  AS content_playout_content ON content_playout_metrics_content_playout.CONTENT_SOURCE_ASSET_ID = content_playout_content.ID"
    )


def test_filter_on_normal_field():
    query = {
        "table": "content_playout_metrics",
        "fields": ["unique_viewers"],
        "filters": [Filter(field="unique_viewers", operator=FilterOperator.gt, value="100")],
    }
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT CONTENT_PLAYOUT_METRICS_VIEW.METRIC_UNIQUE_VIEWERS AS unique_viewers FROM CONTENT_PLAYOUT_METRICS_VIEW WHERE CONTENT_PLAYOUT_METRICS_VIEW.METRIC_UNIQUE_VIEWERS > '100'"
    )


def test_filter_on_join_field():
    query = {
        "table": "content_playout_metrics",
        "fields": ["unique_viewers", "content_title"],
        "filters": [Filter(field="content_title", operator=FilterOperator.eq, value="Liz Pede Bis")],
    }
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT CONTENT_PLAYOUT_METRICS_VIEW.METRIC_UNIQUE_VIEWERS AS unique_viewers, content_playout_content.title FROM CONTENT_PLAYOUT_METRICS_VIEW JOIN DW_DIM.CONTENT_PLAYOUT  AS content_playout_metrics_content_playout ON CONTENT_PLAYOUT_METRICS_VIEW.DIM_CONTENT_PLAYOUT_ID = content_playout_metrics_content_playout.ID JOIN DW_DIM.AMAGI_ASSET  AS content_playout_content ON content_playout_metrics_content_playout.CONTENT_SOURCE_ASSET_ID = content_playout_content.ID WHERE content_playout_content.title = 'Liz Pede Bis'"
    )


def test_filter_on_aggregate_having_clause():
    query = {
        "table": "distribution_metrics",
        "fields": ["channel_id", "avg_viewership_minutes"],
        "filters": [Filter(field="avg_viewership_minutes", operator=FilterOperator.gt, value="100")],
    }
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT viewership_metrics_day_level.dim_channel_id AS channel_id, SUM(viewership_metrics_day_level.METRIC_VIEWERSHIP_MINUTES) AS avg_viewership_minutes FROM viewership_metrics_day_level GROUP BY viewership_metrics_day_level.dim_channel_id HAVING avg_viewership_minutes > '100'"
    )


def test_sort_on_aggregates():
    query = {
        "table": "distribution_metrics",
        "fields": ["channel_id", "avg_viewership_minutes"],
        "filters": [Filter(field="avg_viewership_minutes", operator=FilterOperator.gt, value="100")],
        "sort": SortOrder(field="avg_viewership_minutes", direction="DESC"),
    }
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT viewership_metrics_day_level.dim_channel_id AS channel_id, SUM(viewership_metrics_day_level.METRIC_VIEWERSHIP_MINUTES) AS avg_viewership_minutes FROM viewership_metrics_day_level GROUP BY viewership_metrics_day_level.dim_channel_id HAVING avg_viewership_minutes > '100' ORDER BY avg_viewership_minutes DESC"
    )


def test_offset():
    query = {"table": "distribution_metrics", "fields": ["channel_id"], "offset": 10}
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT viewership_metrics_day_level.dim_channel_id AS channel_id FROM viewership_metrics_day_level OFFSET 10"
    )


def test_limit():
    query = {"table": "distribution_metrics", "fields": ["channel_id"], "limit": 10}
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT viewership_metrics_day_level.dim_channel_id AS channel_id FROM viewership_metrics_day_level LIMIT 10"
    )


def test_in_filter():
    query = {
        "table": "distribution_metrics",
        "fields": ["channel_id"],
        "filters": [Filter(field="channel_id", operator=FilterOperator.in_, value=["1", "2", "3"])],
    }
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT viewership_metrics_day_level.dim_channel_id AS channel_id FROM viewership_metrics_day_level WHERE viewership_metrics_day_level.dim_channel_id in ('1','2','3')"
    )


def test_list_agg():
    query = {"table": "content_playout_metrics", "fields": ["content_title", "genre"], "filters": [], "limit": 10}
    query = SQLQuery(**query)
    sql = builder.build_sql(query)
    assert (
        sql
        == "SELECT content_playout_content.title, listagg(DISTINCT genre.name, ',') AS genre FROM CONTENT_PLAYOUT_METRICS_VIEW JOIN DW_DIM.CONTENT_PLAYOUT  AS content_playout_metrics_content_playout ON CONTENT_PLAYOUT_METRICS_VIEW.DIM_CONTENT_PLAYOUT_ID = content_playout_metrics_content_playout.ID JOIN DW_DIM.AMAGI_ASSET  AS content_playout_content ON content_playout_metrics_content_playout.CONTENT_SOURCE_ASSET_ID = content_playout_content.ID JOIN DW_DIM.GENRE_MAPPINGS  AS genre_mappings ON content_playout_content.id = genre_mappings.asset_id JOIN DW_DIM.GENRE  AS genre ON genre_mappings.GENRE_ID = genre.ID GROUP BY content_playout_content.title LIMIT 10"
    )


# def test_filter_on_normal_field():
#     sql = builder.build_sql('Order', ['ID'], [Filter(field='ID', operator='=', value='5')])
#     assert sql == "SELECT orders.order_id AS ID FROM orders WHERE orders.order_id = '5'"

# def test_sort_order():
#     sql = builder.build_sql('Order', ['ID'], sort=SortOrder(field='ID', direction='DESC'))
#     assert sql == "SELECT orders.order_id AS ID FROM orders ORDER BY orders.order_id DESC"

# def test_limit():
#     sql = builder.build_sql('Order', ['ID'], limit=10)
#     assert sql == "SELECT orders.order_id AS ID FROM orders LIMIT 10"

# You can continue to add more test cases as necessary based on the functionality and edge cases you want to cover.


# def test_simple_field_selection():
#     sql = builder.build_sql('Order', ['ID'])
#     assert sql == "SELECT orders.order_id AS ID FROM orders"

# def test_related_field_selection():
#     sql = builder.build_sql('Order', ['ID', 'UserName'])
#     assert sql == "SELECT orders.order_id AS ID, users.user_name AS UserName FROM orders JOIN users ON orders.user_id = users.id"

# def test_aggregate_field_selection():
#     sql = builder.build_sql('Order', ['TotalAmount'])
#     assert sql == "SELECT SUM(orders.amount) AS TotalAmount FROM orders"

# def test_filter_on_aggregate():
#     sql = builder.build_sql('Order', ['TotalAmount'], [Filter(field='TotalAmount', operator='>', value='100')])
#     assert sql == "SELECT SUM(orders.amount) AS TotalAmount FROM orders HAVING SUM(orders.amount) > '100'"

# def test_filter_on_normal_field():
#     sql = builder.build_sql('Order', ['ID'], [Filter(field='ID', operator='=', value='5')])
#     assert sql == "SELECT orders.order_id AS ID FROM orders WHERE orders.order_id = '5'"

# def test_sort_order():
#     sql = builder.build_sql('Order', ['ID'], sort=SortOrder(field='ID', direction='DESC'))
#     assert sql == "SELECT orders.order_id AS ID FROM orders ORDER BY orders.order_id DESC"

# def test_limit():
#     sql = builder.build_sql('Order', ['ID'], limit=10)
#     assert sql == "SELECT orders.order_id AS ID FROM orders LIMIT 10"

# # You can continue to add more test cases as necessary based on the functionality and edge cases you want to cover.
