
from .AppSettings import AppSettings, Conversation,ConversationMessage
from api.models.Connections import Connection
CONST_TABLE_NAME_APP_SETTINGS = "app-settings"
CONST_TABLE_NAME_CONVERSATION = "conversation"
CONST_TABLE_NAME_CONVERSATION_MESSAGE = "conversation-message"
CONST_TABLE_NAME_CONNECTIONS = "connections"
collection_to_model_map = {
    CONST_TABLE_NAME_APP_SETTINGS: AppSettings,
    CONST_TABLE_NAME_CONVERSATION:Conversation,
    CONST_TABLE_NAME_CONVERSATION_MESSAGE:ConversationMessage,
    CONST_TABLE_NAME_CONNECTIONS:Connection
}