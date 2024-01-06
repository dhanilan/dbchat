import json
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser
import openai

from db_chat.sql_builder.schema import Schema

prompt = ChatPromptTemplate.from_template("find top 10 customers by revenue")
model = ChatOpenAI(openai_api_key="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")

openai.api_key = "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"
# chain = prompt | model


def get_tools():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "FetchData",
                "description": "A method to fetch data from a database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "The table to fetch from"},
                        "columns": {
                            "type": "array",
                            "description": "The columns to fetch",
                            "items": {
                                "anyOf": [
                                    {
                                        "type": "string",
                                        "description": "The column to fetch. The column will be fetched as is. Allowed values are from the columns that are present in table only",
                                    },
                                    {
                                        "type": "object",
                                        "properties": {
                                            "func": {
                                                "type": "string",
                                                "enum": ["count", "sum", "avg", "min", "max"],
                                                "description": "The function to apply to the columns and constants passed as parameters",
                                            },
                                            "params": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string",
                                                    "description": "The columns to pass as parameters to the function or a constant value",
                                                },
                                            },
                                            "label": {"type": "string"},
                                        },
                                    },
                                ]
                            },
                        },
                        "filters": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "field": {
                                        "type": "string",
                                        "description": "The field to filter on",
                                    },
                                    "operator": {
                                        "type": "string",
                                        "enum": ["eq", "neq", "gt", "lt", "gte", "lte", "like", "in"],
                                    },
                                    "value": {"type": "string"},
                                },
                                "required": ["field", "operator", "value"],
                            },
                        },
                        "group_by": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "The Fields to group by",
                        },
                        "sort": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "field": {
                                        "type": "string",
                                        "description": "The field to sort on",
                                    },
                                    "order": {
                                        "type": "string",
                                        "enum": ["asc", "desc"],
                                    },
                                },
                            },
                            "limit": {
                                "type": "integer",
                                "description": "The limit to apply",
                            },
                            "offset": {
                                "type": "integer",
                                "description": "The offset to apply",
                            },
                        },
                    },
                },
            },
        }
    ]

    return tools


tools = get_tools()


def build_context(schema: Schema):
    context = """You will be provided with a schema and your task is to find the right function and its parameters to call.
    Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.

    This is a database of social media application with the following tables:"""
    for table in schema.tables:
        context += "\n" + table + " with the following columns:"
        for column in schema.tables[table].columns:
            context += "\n" + column.name

    context += "\n\n make sure to use only the columns that are listed here only."
    return context


def build_open_ai_query(schema: Schema, question: str):
    messages = []
    context = build_context(schema)
    messages.append(
        {
            "role": "system",
            "content": context,
        }
    )

    messages.append({"role": "user", "content": question})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        temperature=0,
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )

    # print(response)
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors

        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_args = json.loads(tool_call.function.arguments)
            print(function_args)
