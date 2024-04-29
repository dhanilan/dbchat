import os
from typing import Annotated


from autogen import AssistantAgent, UserProxyAgent, register_function

from autogen.cache import Cache

from db_chat.sql_builder.schema import Schema, Query

# tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


config_list = [{"model": "gpt-4-1106-preview", "api_key":os.environ["OPENAI_API_KEY"]}]


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

def sql_executor_tool(query: Annotated[Query, "The query that will be executed"]) -> Annotated[str, "The result of the query"]:
    return 24


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
    return ReAct_prompt.format(input=context["question"])



user_proxy = UserProxyAgent(
    name="User",
    is_termination_msg=lambda x: x.get("content", "") and (x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "") == "MORE_INFO_NEEDED"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,

)



assistant = AssistantAgent(
    name="Assistant",

    system_message="Only use the tools you have been provided with. Reply TERMINATE when the task is done.Reply MORE_INFO_NEEDED if you need more information along with the question to the user.",
    llm_config={"config_list": config_list, "cache_seed": None},
)

# Register the search tool.
register_function(
    sql_executor_tool,
    caller=assistant,
    executor=user_proxy,
    name="sql_executor_tool",
    description="""Exectues the given query against the database and returns the result. The query should follow the rules below:
    1. The argument will only contain the below listed keys
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
    7. `offset` key will contain the number of rows to offset the result by""",
)

# Cache LLM responses. To get different responses, change the cache_seed value.

def ask_llm(question:str, schema:Schema):
    with Cache.disk(cache_seed=43) as cache:
        result = user_proxy.initiate_chat(
            assistant,
            message=react_prompt_message,
            question=question,
            schema_description=build_schema_prompt(schema),
            cache=cache,
            summary_method="reflection_with_llm"

        )
        print(result)
        return result
