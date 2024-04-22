import logging
import os

from . import Agent
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from events.project_status_message import IdentifiedProjectStatusMessageEvent, RespondProjectStatusMessageEvent

class Github(Agent):
    def __init__(self):
        os.environ["GITHUB_APP_ID"] = os.getenv("APP_ID")
        os.environ["GITHUB_APP_PRIVATE_KEY"] = os.getenv("APP_PRIVATE_KEY")
        os.environ["GITHUB_BRANCH"] = "bot-branch"
        os.environ["GITHUB_BASE_BRANCH"] = "main"
        tools = GitHubToolkit.from_github_api_wrapper(GitHubAPIWrapper()).get_tools()
        super().__init__(tools, legacy=True)

    def _handle_event(self, event):
        super()._handle_event(event)
        if isinstance(event, IdentifiedProjectStatusMessageEvent):
            self._handle_identified_project_status_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    def _handle_identified_project_status_message_event(self, event: IdentifiedProjectStatusMessageEvent):
        questions = [
            "what is the total number of issues for the project?",
            "how many issues are open for the project?",
            "how many issues are closed for the project?",
            "how many issues are in progress for the project?",
        ]
        # output = self._run_chain(prompt="znas/process_project_status_message",
        #                          input={"project": event.project, "message_content": event.message_content})
        output = self._invoke_prompt(prompt="znas/answer_project_status_message_question",
                                     input={"project": event.project, "question": questions[2]})
        self._emit_event(RespondProjectStatusMessageEvent(**output))
        