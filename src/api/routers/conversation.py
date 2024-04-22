from datetime import datetime
from fastapi import APIRouter, Depends
from api.settings import settings
from api.models.model_map import CONST_TABLE_NAME_CONVERSATION,CONST_TABLE_NAME_CONVERSATION_MESSAGE
from api.models.AppSettings import Conversation,ConversationMessage
from api.dependencies import getRepository
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
    repository.delete_by_model({"id":id})
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

    response = ConversationMessage(
                                   text= f' response from bot for :{conversation_message.text}',
                                   sender="bot",
                                   timestamp=datetime.now(),
                                   conversation_id=conversation_id
                                   )
    repository.create(response)

    return response.model_dump()

