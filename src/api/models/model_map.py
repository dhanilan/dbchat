
from .AppSettings import AppSettings, Conversation,ConversationMessage

CONST_TABLE_NAME_APP_SETTINGS = "app-settings"
CONST_TABLE_NAME_CONVERSATION = "conversation"
CONST_TABLE_NAME_CONVERSATION_MESSAGE = "conversation-message"
collection_to_model_map = {
    CONST_TABLE_NAME_APP_SETTINGS: AppSettings,
    CONST_TABLE_NAME_CONVERSATION:Conversation,
    CONST_TABLE_NAME_CONVERSATION_MESSAGE:ConversationMessage
}