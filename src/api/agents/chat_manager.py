from autogen import ConversableAgent
from api.models.AppSettings import ConversationMessage,AppSettings


class ChatManager:
    def __init__(self,app_settings: AppSettings):
        self.app_settings = app_settings

    def get_response(self, conversation_id:str,message:ConversationMessage):

        agent = ConversableAgent(
            "chatbot",
            llm_config={"config_list": [{"model": "gpt-4", "api_key": self.app_settings.oai_api_key}]},
            code_execution_config=False,  # Turn off code execution, by default it is off.
            function_map=None,  # No registered functions, by default it is None.
            human_input_mode="NEVER",  # Never ask for human input.
        )
        response =  agent.generate_reply(messages=[{"content": message.text, "role": "user"}])
        return response