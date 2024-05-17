import os
from typing import Annotated
import json

from autogen import AssistantAgent, UserProxyAgent, register_function

from autogen.cache import Cache
from sqlalchemy import create_engine, text

from db_chat.sql_builder.Filter import Filter
from db_chat.sql_builder.Query import Expression
from db_chat.sql_builder.schema import Schema, Query
from db_chat.sql_builder.sqlalchemy_query_builder import SQLAlchemyQueryBuilder
import traceback
# tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


# config_list = [{"model": "gpt-4-1106-preview", "api_key":os.environ["OPENAI_API_KEY"]}]


def log_query_from_llm(query: str):
    with open("llm_queries.txt", "a") as f:
        f.write(query + "\n")
def log_exception_from_llm(query:Query,exception: str):
    print(exception)
    with open("llm_exceptions.txt", "a") as f:
        f.write("==============================: \n")
        f.write("Exception occured for query: \n")
        if isinstance(query,Query):
            f.write(""+   query.model_dump_json() + "\n")
        else:
            f.write(""+  json.dumps( query) + "\n")
        f.write("Exception is: " + "\n")
        f.write(exception + "\n")


def get_sql_executor_tool(schema: Schema,connection_string:str):

    def sql_executor_tool(query: Annotated[Query, "The query that will be executed"]) -> Annotated[str, "The result of the query"]:


        query_builder = SQLAlchemyQueryBuilder(schema)

        try:
            query = Query.model_validate(query)

            validation_errors = query_builder.validate(query)
            if validation_errors and len(validation_errors) > 0:
                raise ValueError(validation_errors)

            sql = query_builder.build_query(query)
        except Exception as e:
            log_exception_from_llm(query,traceback.format_exc())

            return "error occured durring execution" + str(e)

        print(sql)
        try:
            engine = create_engine(connection_string)

            with engine.connect() as connection:
                result = connection.execute(text(sql))
                fetched_results = result.fetchall()

            result_as_string = ""
            for row in fetched_results:
                for column in row:
                    result_as_string += str(column) + " "
                result_as_string += "\n"


            return result_as_string
        except Exception as e:
            return "error occured durring execution" + str(e)
    return sql_executor_tool

def build_schema_prompt(schema: Schema):
    """
    Build the prompt for the LLM model
    """
    prompt = "Schema :\n"
    prompt += "Here are the list of tables and their columns:\n"
    for table in schema.tables.values():
        prompt += f"{table.name} - "
        for column in table.columns:
            prompt += f"{column.name},"

        prompt += "\n"
    return prompt

# def sql_executor_tool(query: Annotated[Query, "The query that will be executed"]) -> Annotated[str, "The result of the query"]:
#     return 24


# NOTE: this ReAct prompt is adapted from Langchain's ReAct agent: https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/agents/react/agent.py#L79
ReAct_prompt = """
You are an Analytics Expert that can help answer questions by looking at the data inside the database. Answer the following questions as best you can. You have access to tools provided.

The following is the schema of the database:
{schema_description}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take
Action Input: the input to the action
Observation: the result of the action
... (this process can repeat multiple times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
Question: {input}
"""

# Define the ReAct prompt message. Assuming a "question" field is present in the context


def react_prompt_message(sender, recipient, context):
    return ReAct_prompt.format(input=context["question"],schema_description=context["schema_description"])



def getUserProxyAgent():
    user_proxy = UserProxyAgent(
        name="User",
        is_termination_msg=lambda x: x.get("content", "") and (x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "") == "MORE_INFO_NEEDED"),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,

    )
    return user_proxy


def getAssistantAgent(config_list):
    assistant = AssistantAgent(
        name="Assistant",

        system_message="""
        Only use the tools you have been provided with. Reply TERMINATE when the task is done.Reply MORE_INFO_NEEDED if you need more information along with the question to the user.

    You will follow these rules while creating a json response:
    1. The json response will only contain the below listed keys
    2. `table` key will contain the name of the table to fetch the data from
    3. `joins` - dictionary of joins to apply to the query, where key is the alias of join. Each join will have the following keys
            3.a. `type` -  Allowed values are `inner`, `left`, `right`, `full`
            3.b. `table` - Name of the table to join with
            3.c. `field` - Field of the current table to join with
            3.d. `related_field` - Field of the joined table to join with

    3. `fields` key will contain the list of fields to fetch from the chosen table.Join fields are represented `join alias`.`field` . Fields of each table will be listed in a separate list after the rules. Join fields will be listed in the same list as the table fields.
    4. `filters` key will contain the list of filters to apply to the query. Each filter will have a 'field', 'operator' and 'value'. Allowed operators are 'eq', 'neq', 'gt', 'lt', 'gte', 'lte', 'like'
    5. `sort` -  will  have a 'field' and 'direction'.
        4.a. `field` - Field to sort to sort by. Use columns from the chosen `table` only . Do not make up new columns.
        4.b. `direction` - Allowed direction are 'asc' and 'desc'.
    6. `limit` key will contain the number of rows to limit the result to
    7. `offset` key will contain the number of rows to offset the result by
    """,
        llm_config={"config_list": config_list, "cache_seed": None},
    )
    return assistant

def register_agent(assistant,user_proxy,schema, connection_string):
    sql_executor_tool = get_sql_executor_tool(schema,connection_string)
# Register the search tool.
    register_function(
        sql_executor_tool,
        caller=assistant,
        executor=user_proxy,
        name="sql_executor_tool",
        description="""Exectues the given query against the database and returns the result. """,
    )

# Cache LLM responses. To get different responses, change the cache_seed value.

def ask_llm(question:str, schema:Schema,api_key:str,connection_string:str=None):
    config_list = [{"model": "gpt-4-1106-preview", "api_key": api_key}]
    assistant = getAssistantAgent(config_list)
    user_proxy = getUserProxyAgent()
    register_agent(assistant,user_proxy,schema,connection_string)
    # with Cache.disk(cache_seed=45) as cache:
    result = user_proxy.initiate_chat(
        assistant,
        message=react_prompt_message,
        question=question,
        schema_description=build_schema_prompt(schema),
        # cache=cache,
        summary_method="reflection_with_llm"

    )
        # print(result.summary)
    return result.summary
