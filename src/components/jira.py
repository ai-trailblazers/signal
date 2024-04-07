import logging

from reactivex import Subject, interval
from reactivex.disposable import Disposable
from langchain.agents import AgentType, initialize_agent
from langchain_openai import OpenAI
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage

class Jira(Subject):
    def __init__(self):
        super().__init__()
        self.jira_scanner: Disposable = None
        self.agent = None
        self.__create_agent()

    def start(self, interval_seconds):
        if self.jira_scanner:
            self.jira_scanner.dispose()
        self.jira_scanner = interval(interval_seconds).pipe(
            map(lambda _: self.__scan_jira_projects())
        ).subscribe()

    def on_next(self, event):
        if isinstance(event, IdentifiedProjectStatusMessage):
            self.__handle_identified_project_status_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    def on_error(self, error):
        logging.error(error)

    def stop(self):
        if self.jira_scanner:
            self.jira_scanner.dispose()
        self.dispose()

    def __create_agent(self):
        if self.agent:
            return
        self.agent = initialize_agent(tools=JiraToolkit.from_jira_api_wrapper(JiraAPIWrapper()).get_tools(),
                                      llm=OpenAI(),
                                      agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                      verbose=True)

    def __handle_identified_project_status_message_event(self, event: IdentifiedProjectStatusMessage):
        logging.debug(f"Handling '{type(event).__name__}' event.")

        # todo : use Langchain Jira toolkit to compose a status report
        mockRespondProjectStatusMessage = RespondProjectStatusMessage()

        logging.debug(f"Emmiting '{type(mockRespondProjectStatusMessage).__name__}' event.")

        # Emmit event to respond to a project status message.
        super().on_next(mockRespondProjectStatusMessage)

    def __scan_jira_projects():
        pass
