from autogen import ConversableAgent, AssistantAgent
from api.models.AppSettings import ConversationMessage,AppSettings, Conversation
from api.models.Connections import Connection
from api.agents.autogen.react_agents import ask_llm


class ChatManager:
    def __init__(self,app_settings: AppSettings):
        self.app_settings = app_settings
        self.llm_config = {"config_list": [{"model": "gpt-4", "api_key": self.app_settings.oai_api_key}]}

    def get_response(self, conversation:Conversation,message:ConversationMessage,connection:Connection):
        response = ask_llm(message.text, connection.connection_schema, self.app_settings.oai_api_key)
        # agent = ConversableAgent(
        #     "chatbot",
        #     llm_config=self.llm_config,
        #     code_execution_config=False,  # Turn off code execution, by default it is off.
        #     function_map=None,  # No registered functions, by default it is None.
        #     human_input_mode="NEVER",  # Never ask for human input.
        # )
        # response =  agent.generate_reply(messages=[{"content": message.text, "role": "user"}])
        return response

    def getChatManager(self):
        return self

    def get_planner_agent(self):
        return AssistantAgent(
            "planner",
            system_message="You are a helpful assistant. You will help break down the tasks and provide guidance on how to complete them."
            "A user will ask a question about the data in the database and you will provide the set of tasks to break down into sub tasks."
            "Each task will be broken down into sub tasks and you will provide guidance on how to complete them."
            "Respond with a list of tasks to complete the user's request.",
            llm_config={"config_list": [{"model": "gpt-4", "api_key": self.app_settings.oai_api_key}]},
            code_execution_config=False,  # Turn off code execution, by default it is off.
            function_map=None,  # No registered functions, by default it is None.
            human_input_mode="NEVER",  # Never ask for human input.
        )

    def run(self):
        pass