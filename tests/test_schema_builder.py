from db_chat.sql_builder.schema import build_schema


def test_simple_field_selection():
    connection_string = "postgresql://postgres:postgres@localhost/postgres"
    schema_builder = build_schema(connection_string)

    print(schema_builder)
    assert 1 == 1
