from db_chat.sql_builder.schema import build_schema
from db_chat.llm.classic_prompt import build_prompt
from db_chat.sql_builder.sqlalchemy_query_builder import SQLAlchemyQueryBuilder
from sqlalchemy import create_engine, text


def ask_ai(connection_string: str, question: str):
    schemmm = build_schema(connection_string)
    query = build_prompt(schema=schemmm, question=question)
    query_builder = SQLAlchemyQueryBuilder(schema=schemmm)
    sql = query_builder.build_query(query=query)
    engine = create_engine(connection_string)

    with engine.connect() as connection:
        result = connection.execute(text(sql))
        fetched_results = result.fetchall()

    for row in fetched_results:
        print(row)
