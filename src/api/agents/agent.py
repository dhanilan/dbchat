
from typing import List

from api.models import Conversation, ConversationMessage,AppSettings,ConversationWithMessages
from openai import OpenAI

class SQLAgentOrchestrator:
    def __init__(self, settings: AppSettings):
        self.settings = settings

    def respond(self, conversation: ConversationWithMessages, message: ConversationMessage) -> ConversationMessage:
        client = OpenAI(self.settings.oai_api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
                {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                {"role": "user", "content": "Where was it played?"}
            ]
        )

