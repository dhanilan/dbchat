from datetime import datetime
from fastapi import APIRouter, Depends
from api.agents.autogen.react_agents import get_sql_executor_tool
from api.models.Connections import Connection
from api.settings import settings
from api.models.model_map import CONST_TABLE_NAME_APP_SETTINGS, CONST_TABLE_NAME_CONVERSATION,CONST_TABLE_NAME_CONVERSATION_MESSAGE,CONST_TABLE_NAME_CONNECTIONS
from api.models.AppSettings import AppSettings, Conversation,ConversationMessage
from api.dependencies import getRepository
from api.agents.chat_manager import ChatManager

router = APIRouter()

@router.get("/conversation/", tags=["conversation"])
async def read_conversation(customer_id: str = "default"):

    repository = getRepository(CONST_TABLE_NAME_CONVERSATION,settings)
    conversation  = repository.get_by_model({"customer_id":customer_id})
    return conversation

@router.post("/conversation/", tags=["conversation"])
async def create_conversation(conversation: Conversation):

    repository = getRepository(CONST_TABLE_NAME_CONVERSATION,settings)
    repository.create(conversation)

    return conversation.id

@router.get("/conversation/{id}", tags=["conversation"])
async def read_conversation(id: str):

    repository = getRepository(CONST_TABLE_NAME_CONVERSATION,settings)
    conversation  = repository.get_one_by_model({"id":id})
    return conversation



@router.delete("/conversation/{id}", tags=["conversation"])
async def delete_conversation(id: str):

    repository = getRepository(CONST_TABLE_NAME_CONVERSATION,settings)
    repository.delete_by_id(id)
    return {"success": True}


@router.get("/conversation/{conversation_id}/messages", tags=["conversation"])
async def read_conversation_messages(conversation_id: str):

    repository = getRepository(CONST_TABLE_NAME_CONVERSATION_MESSAGE,settings)
    conversation_messages  = repository.get_by_model({"conversation_id":conversation_id})
    return conversation_messages

@router.post("/conversation/{conversation_id}/messages", tags=["conversation"])
async def create_conversation_message(conversation_message: ConversationMessage,conversation_id: str):

    repository = getRepository(CONST_TABLE_NAME_CONVERSATION_MESSAGE,settings)
    repository.create(conversation_message)

    conversationRepository = getRepository(CONST_TABLE_NAME_CONVERSATION,settings)
    conversation : Conversation = conversationRepository.get_by_id(conversation_id)

    appSettingsRepository = getRepository(CONST_TABLE_NAME_APP_SETTINGS,settings)
    app_settings:AppSettings  = appSettingsRepository.get_one_by_model({"customer_id":conversation.customer_id})

    connectionRepository = getRepository(CONST_TABLE_NAME_CONNECTIONS,settings)
    connection:Connection = connectionRepository.get_by_id(conversation.connection_id)



    import json
    query = json.loads("""
 {
  "table": "invoice",
  "fields": [
    "customer_id",
    {
      "func": "sum",
      "parameters": ["total"],
      "alias": "total_amount"
    }
  ],
  "joins": {
    "customer": {
      "type": "inner",
      "table": "customer",
      "field": "customer_id",
      "related_field": "customer_id"
    }
  },
  "group_by": ["customer_id"],
  "sort": {
    "field": "total_amount",
    "direction": "desc"
  },
  "limit": 1
}
    """)
    # result = get_sql_executor_tool(connection.connection_schema,connection.connection_string)(query)
    # print(result)
    # return result
#     raise "Not implemented yet."

    if (app_settings is None or app_settings.oai_api_key is None or  app_settings.oai_api_key == ""):
        response = ConversationMessage(
                                   text= f"Please provide an API Key in the settings to use the chatbot.",
                                   sender="system",
                                   timestamp=datetime.now(),
                                   conversation_id=conversation_id
                                   )
    else:
        chat_manager = ChatManager(app_settings)
        response_message = chat_manager.get_response(conversation,conversation_message,connection)

        response = ConversationMessage(
                                    text= f'{response_message}',
                                    sender="bot",
                                    timestamp=datetime.now(),
                                    conversation_id=conversation_id
                                    )
    repository.create(response)

    return response.model_dump()

