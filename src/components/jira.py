import logging

from . import Agent
from typing import cast
from langchain import hub
from langchain.agents import AgentType, initialize_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage

class Jira(Agent):
    def __init__(self):
        super().__init__()

    def _handle_event(self, event):
        if isinstance(event, IdentifiedProjectStatusMessage):
            self._handle_identified_project_status_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    def _handle_identified_project_status_message_event(self, event: IdentifiedProjectStatusMessage):
        logging.debug(f"Handling '{type(event).__name__}' event.")

        result = self._invoke_prompt(prompt="znas/process_project_status_message",
                                     input=event.content["input"],
                                     author=event.content["author"])
        content = {
            "input": result["output"],
            "placeholder": "just a placeholder for now"
        }

        respondProjectStatusMessage = RespondProjectStatusMessage(content=content)

        logging.debug(f"Emmiting '{type(respondProjectStatusMessage).__name__}' event.")

        # Emit event to respond to a project status message.
        super().on_next(respondProjectStatusMessage)
