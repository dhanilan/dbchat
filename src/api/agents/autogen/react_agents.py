import os
from typing import Annotated


from autogen import AssistantAgent, UserProxyAgent, register_function

from autogen.cache import Cache
from sqlalchemy import create_engine, text

from db_chat.sql_builder.Filter import Filter
from db_chat.sql_builder.Query import Expression
from db_chat.sql_builder.schema import Schema, Query
from db_chat.sql_builder.sqlalchemy_query_builder import SQLAlchemyQueryBuilder

# tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


# config_list = [{"model": "gpt-4-1106-preview", "api_key":os.environ["OPENAI_API_KEY"]}]

def get_sql_executor_tool(schema: Schema,connection_string:str):

    def sql_executor_tool(query: Annotated[Query, "The query that will be executed"]) -> Annotated[str, "The result of the query"]:
        query_builder = SQLAlchemyQueryBuilder(schema)
        query = Query(**query)
        for index,field in enumerate( query.fields):
            if isinstance(field, str):
                continue
            else:
                query.fields[index] = Expression(**field)

        for index,filter in enumerate(query.filters):
            query.filters[index] = Filter(**filter)

        validation_errors = query_builder.validate(query)
        if validation_errors and len(validation_errors) > 0:
            raise ValueError(validation_errors)
        sql = query_builder.build_query(query)

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

        system_message="Only use the tools you have been provided with. Reply TERMINATE when the task is done.Reply MORE_INFO_NEEDED if you need more information along with the question to the user.",
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
