#pydantic model for settings
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from api.models.BaseDbModel import BaseDbModel


class AppSettings(BaseModel,BaseDbModel):
    oai_api_key: str=None
    analytics_db_url: str=None
    customer_id: str = "default"

class ConversationMessage(BaseModel,BaseDbModel):
    text: str
    sender: str
    timestamp: datetime
    conversation_id: str

class Conversation(BaseModel,BaseDbModel):
    customer_id: str = "default"
    title : str = ""
