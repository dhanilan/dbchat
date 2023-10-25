class Relationship:
    def __init__(self, name: str, table1: str, field1: str, table2: str, field2: str):
        self.name = name
        self.table1 = table1
        self.field1 = field1
        self.table2 = table2
        self.field2 = field2


class UserFriendlyMappings:
    def __init__(self, fields: list[str], metrics: list[str], aggregate_metrics: list[str]):
        self.fields = fields
        self.metrics = metrics
        self.aggregate_metrics = aggregate_metrics

    def to_dict(self):
        return {"fields": self.fields, "metrics": self.metrics, "aggregate_metrics": self.aggregate_metrics}


table_mapping = {
    "distribution_metrics": "DW_METRICS.viewership_metrics",
    "channel": "DW_DIM.channel",
    "content_playout_metrics": "DW_METRICS.CONTENT_PLAYOUT_METRICS_VIEW",
    "content_playout": "DW_DIM.CONTENT_PLAYOUT",
    "delivery": "DW_DIM.DELIVERY",
    "customer": "DW_DIM.CUSTOMER",
    "content": "DW_DIM.AMAGI_ASSET",
    "genre": "DW_DIM.GENRE",
    "genre_mappings": "DW_DIM.GENRE_MAPPINGS",
    "region": "DW_DIM.REGION_DEFINITION",
    "platform": "DW_DIM.PLATFORM",
    "content_playout_metrics_minute_level": "CONTENT_PLAYOUT_MINUTE_LEVEL_METRICS_VIEW",
}

field_mappings = {
    "distribution_metrics": {
        "timestamp": "wallclock_time",
        "channel_id": "dim_channel_id",
        "platform_id": "dim_platform_id",
        "granularity": "DIM_TIME_GRANULARITY",
        "channel_name": {"relationships": ["distribution_channel"], "field": "name"},
        "country": {"relationships": ["distribution_region"], "field": "COUNTRY"},
        "city": {"relationships": ["distribution_region"], "field": "CITY"},
        "division": {"relationships": ["distribution_region"], "field": "DIVISION"},
        "postal_code": {"relationships": ["distribution_region"], "field": "POSTAL_CODE"},
        # Metrics
        "unique_viewers": "metric_unique_viewers",
        "total_unique_viewers": {"aggregate": "SUM", "field": "metric_unique_viewers"},
        "viewership_minutes": "METRIC_VIEWERSHIP_MINUTES",
        "avg_viewership_minutes": {"aggregate": "AVG", "field": "METRIC_VIEWERSHIP_MINUTES"},
        "total_viewership_minutes": {"aggregate": "SUM", "field": "METRIC_VIEWERSHIP_MINUTES"},
        "session_count": "METRIC_SESSION_COUNT",
        # TODO: change to session_duration_minutes
        "session_duration_minutes": "METRIC_AVG_UNIQUE_VIEWERS_ENGAMENT_TIME",
        "avg_session_duration_minutes": {"aggregate": "AVG", "field": "METRIC_AVG_UNIQUE_VIEWERS_ENGAMENT_TIME"},
        "minute_audience": "METRIC_AVG_UNIQUE_VIEWERS_ENGAMENT_TIME",
        "avg_minute_audience": {"aggregate": "AVG", "field": "METRIC_AVG_UNIQUE_VIEWERS_ENGAMENT_TIME"},
    },
    "channel": {"id": "id", "name": "name"},
    "content_playout_metrics": {
        # content genre
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
        # content playout info
        "content_playout_id": "DIM_CONTENT_PLAYOUT_ID",
        "content_playout_start_time": {
            "relationships": ["content_playout_metrics_content_playout"],
            "field": "start_time",
        },
        "content_playout_end_time": {"relationships": ["content_playout_metrics_content_playout"], "field": "end_time"},
        "content_playout_duration_minutes": {
            "relationships": ["content_playout_metrics_content_playout"],
            "field": "duration",
        },
        "channel_id": {
            "relationships": [
                "content_playout_metrics_content_playout",
                "content_playout_delivery",
                "delivery_channel",
            ],
            "field": "id",
        },
        "channel_name": {
            "relationships": [
                "content_playout_metrics_content_playout",
                "content_playout_delivery",
                "delivery_channel",
            ],
            "field": "name",
        },
        "platform_id": {
            "relationships": [
                "content_playout_metrics_content_playout",
                "content_playout_delivery",
                "delivery_platform",
            ],
            "field": "id",
        },
        "platform_name": {
            "relationships": [
                "content_playout_metrics_content_playout",
                "content_playout_delivery",
                "delivery_platform",
            ],
            "field": "name",
        },
        # metrics
        "unique_viewers": "METRIC_UNIQUE_VIEWERS",
        "viewership_minutes": "METRIC_VIEWERSHIP_MINUTES",
        # aggregate metrics
        "total_unique_viewers": {"aggregate": "SUM", "field": "METRIC_UNIQUE_VIEWERS"},
        "avg_unique_viewers": {"aggregate": "AVG", "field": "METRIC_UNIQUE_VIEWERS"},
        "total_viewership_minutes": {"aggregate": "SUM", "field": "METRIC_VIEWERSHIP_MINUTES"},
        "avg_watch_percentage": {
            "aggregate": "AVG",
            "field": "METRIC_AVG_UNIQUE_VIEWERS_ENGAMENT_TIME",  # TODO: change to METRIC_WATCH_PERCENTAGE
        },
        "count_content_playout": {"aggregate": "COUNT", "field": "dim_content_playout_id"},
        "content_channel_names": {
            "aggregate": "listagg",
            "field": "delivery_channel.name",
            "relationships": [
                "content_playout_metrics_content_playout",
                "content_playout_delivery",
                "delivery_channel",
            ],
        },
        "content_platform_names": {
            "aggregate": "listagg",
            "field": "delivery_platform.name",
            "relationships": [
                "content_playout_metrics_content_playout",
                "content_playout_delivery",
                "delivery_platform",
            ],
        },
    },
    "content_playout_metrics_minute_level": {
        # content genre
        "content_title": {
            "relationships": [
                "content_playout_metrics_content_playout_minute_level",
                "content_playout_content_minute_level",
            ],
            "field": "title",
        },
        "content_name": {
            "relationships": [
                "content_playout_metrics_content_playout_minute_level",
                "content_playout_content_minute_level",
            ],
            "field": "name",
        },
        "genre": {
            "aggregate": "listagg",
            "field": "genre.name",
            "relationships": [
                "content_playout_metrics_content_playout_minute_level",
                "content_playout_content_minute_level",
                "genre_mappings_minute_level",
                "genre_minute_level",
            ],
        },
        # content playout info
        "content_playout_id": "DIM_CONTENT_PLAYOUT_ID",
        "content_playout_start_time": {
            "relationships": ["content_playout_metrics_content_playout_minute_level"],
            "field": "start_time",
        },
        "content_playout_end_time": {
            "relationships": ["content_playout_metrics_content_playout_minute_level"],
            "field": "end_time",
        },
        "content_playout_duration_minutes": {
            "relationships": ["content_playout_metrics_content_playout_minute_level"],
            "field": "duration",
        },
        "channel_id": {
            "relationships": [
                "content_playout_metrics_content_playout_minute_level",
                "content_playout_delivery_minute_level",
                "delivery_channel_minute_level",
            ],
            "field": "id",
        },
        "channel_name": {
            "relationships": [
                "content_playout_metrics_content_playout_minute_level",
                "content_playout_delivery_minute_level",
                "delivery_channel_minute_level",
            ],
            "field": "name",
        },
        "platform_id": {
            "relationships": [
                "content_playout_metrics_content_playout_minute_level",
                "content_playout_delivery_minute_level",
                "delivery_platform_minute_level",
            ],
            "field": "id",
        },
        "platform_name": {
            "relationships": [
                "content_playout_metrics_content_playout_minute_level",
                "content_playout_delivery_minute_level",
                "delivery_platform_minute_level",
            ],
            "field": "name",
        },
        # metrics
        "unique_viewers": "METRIC_UNIQUE_VIEWERS",
        "viewership_minutes": "METRIC_VIEWERSHIP_MINUTES",
        # aggregate metrics
        "total_unique_viewers": {"aggregate": "SUM", "field": "METRIC_UNIQUE_VIEWERS"},
        "avg_unique_viewers": {"aggregate": "AVG", "field": "METRIC_UNIQUE_VIEWERS"},
    },
    "content_playout": {"ID": "ID", "DELIVERY_ID": "DELIVERY_ID", "CONTENT_SOURCE_ASSET_ID": "CONTENT_SOURCE_ASSET_ID"},
    "delivery": {"ID": "ID", "CHANNEL_ID": "CHANNEL_ID"},
    "customer": {"amgid": "AMGID", "name": "NAME", "customer_type": "CUSTOMER_TYPE"},
    "content": {
        "name": "NAME",
        "title": "TITLE",
        "title_type": "TITLE_TYPE",
        "episode_number": "EPISODE_NUMBER",
        "season_id": "SEASON_ID",
        "language": "LANGUAGE",
        "id": "id",
    },
    "genre": {"NAME": "NAME"},
    "genre_mappings": {},
    "region": {
        "id": "ID",
        "country": "COUNTRY",
        "city": "CITY",
        "division": "DIVISION",
        "postal_code": "POSTAL_CODE",
        "continent": "CONTINENT",
    },
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
    Relationship(
        name="distribution_region",
        table1="distribution_metrics",
        field1="DIM_REGION_DEFINITION_ID",
        table2="region",
        field2="ID",
    ),
    Relationship(
        name="content_playout_delivery", table1="content_playout", field1="DELIVERY_ID", table2="delivery", field2="ID"
    ),
    Relationship(name="delivery_channel", table1="delivery", field1="CHANNEL_ID", table2="channel", field2="ID"),
    Relationship(
        name="delivery_platform", table1="delivery", field1="DELIVERY_PLATFORM", table2="platform", field2="ID"
    ),
    Relationship(
        name="content_playout_metrics_content_playout_minute_level",
        table1="content_playout_metrics_minute_level",
        field1="DIM_CONTENT_PLAYOUT_ID",
        table2="content_playout",
        field2="ID",
    ),
    Relationship(
        name="content_playout_content_minute_level",
        table1="content_playout",
        field1="CONTENT_SOURCE_ASSET_ID",
        table2="content",
        field2="ID",
    ),
    Relationship(
        name="genre_mappings_minute_level",
        table1="content_playout_content_minute_level",
        field1="id",
        table2="genre_mappings",
        field2="asset_id",
    ),
    Relationship(
        name="genre_minute_level", table1="genre_mappings_minute_level", field1="GENRE_ID", table2="genre", field2="ID"
    ),
    Relationship(
        name="content_playout_delivery_minute_level",
        table1="content_playout",
        field1="DELIVERY_ID",
        table2="delivery",
        field2="ID",
    ),
    Relationship(
        name="delivery_channel_minute_level", table1="delivery", field1="CHANNEL_ID", table2="channel", field2="ID"
    ),
    Relationship(
        name="delivery_platform_minute_level",
        table1="delivery",
        field1="DELIVERY_PLATFORM",
        table2="platform",
        field2="ID",
    ),
]


# from field_mappings build list of user friendly mappings
user_friendly_mappings = {
    "distribution_metrics": UserFriendlyMappings(
        fields=[
            "channel_name",
            "channel_id",
            "platform_id",
            "timestamp",
            "country",
            "city",
            "division",
            "postal_code",
            "granularity",
        ],
        metrics=[
            "unique_viewers",
            "viewership_minutes",
            "session_count",
            "session_duration_minutes",
            "minute_audience",
        ],
        aggregate_metrics=[
            "avg_viewership_minutes",
            "total_unique_viewers",
            "total_viewership_minutes",
            "avg_session_duration_minutes",
            "avg_minute_audience",
        ],
    ),
    "content_playout_metrics": UserFriendlyMappings(
        fields=[
            "content_playout_id",
            "content_name",
            "content_title",
            "content_playout_start_time",
            "content_playout_end_time",
            "content_playout_duration_minutes",
            "channel_name",
            "channel_id",
            "platform_name",
            "platform_id",
            "genre",
            "content_channel_names",
            "content_platform_names",
        ],
        metrics=["unique_viewers", "viewership_minutes"],
        aggregate_metrics=[
            "total_unique_viewers",
            "avg_unique_viewers",
            "total_viewership_minutes",
            "avg_watch_percentage",
            "count_content_playout",
        ],
    ),
    "content_playout_metrics_minute_level": UserFriendlyMappings(
        fields=[
            "content_playout_id",
            "content_name",
            "content_title",
            "content_playout_start_time",
            "content_playout_end_time",
            "content_playout_duration_minutes",
            "channel_name",
            "channel_id",
            "platform_name",
            "platform_id",
            "genre",
        ],
        metrics=["unique_viewers", "viewership_minutes"],
        aggregate_metrics=["total_unique_viewers", "avg_unique_viewers"],
    ),
    "customer": UserFriendlyMappings(fields=["name", "amgid", "customer_type"], metrics=[], aggregate_metrics=[]),
    "content": UserFriendlyMappings(
        fields=["name", "title", "title_type", "episode_number", "season_id", "language", "id"],
        metrics=[],
        aggregate_metrics=[],
    ),
}
