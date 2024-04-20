import logging
import os

from . import Agent
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage

class Github(Agent):
    def __init__(self):
        os.environ["GITHUB_APP_ID"] = os.getenv("APP_ID")
        os.environ["GITHUB_APP_PRIVATE_KEY"] = os.getenv("APP_PRIVATE_KEY")
        os.environ["GITHUB_BRANCH"] = "bot-branch"
        os.environ["GITHUB_BASE_BRANCH"] = "main"

        tools=GitHubToolkit.from_github_api_wrapper(GitHubAPIWrapper()).get_tools()
        
        super().__init__(legacy=True, tools=tools)

    def _handle_event(self, event):
        super()._handle_event(event)

        if isinstance(event, IdentifiedProjectStatusMessage):
            self._handle_identified_project_status_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    def _handle_identified_project_status_message_event(self, event: IdentifiedProjectStatusMessage):
        result = self._invoke_prompt(prompt="znas/process_project_status_message",
                                     input={"input": event.input, "author": event.author},
                                     tools=self.tools)

        self._emmit_event(RespondProjectStatusMessage(input=result["output"],
                                                      author=event.author))