import logging

from typing import cast
from threading import Lock
from reactivex import Subject, interval
from reactivex.disposable import Disposable
from langchain import hub
from langchain.agents import AgentType, AgentExecutor, initialize_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage

class Jira(Subject):
    def __init__(self):
        super().__init__()

        self.jira_scanner: Disposable = None
        self.agent: AgentExecutor = None
        self.lock = Lock()

        self.__create_agent()

    def start(self, interval_seconds):
        if self.jira_scanner:
            return
        
        self.jira_scanner = interval(interval_seconds).pipe(
            map(lambda _: self.__scan_jira_projects())
        ).subscribe()

    def on_next(self, event):
        if isinstance(event, IdentifiedProjectStatusMessage):
            self._handle_identified_project_status_message_event(event)
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
                                      llm=ChatOpenAI(),
                                      agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                      verbose=True,
                                      handle_parsing_errors=True)

    def _handle_identified_project_status_message_event(self, event: IdentifiedProjectStatusMessage):
        logging.debug(f"Handling '{type(event).__name__}' event.")
        
        prompt = cast(PromptTemplate, hub.pull("znas/process_project_status_message"))
        chain = self.agent | prompt
        content = None

        with self.lock:
            try:
                result = self.agent.invoke({"input": "what is the status of PD2 project?"})
                # result = self.agent.invoke(event.content)
                content = {
                    "input": result["output"]
                }
            except Exception as e:
                # Handle the exception, e.g., by logging it
                logging.error(f"An error occurred while invoking the chain: {e}")
                return  # Optionally return early if the error means the rest of the function should not execute

            # If no exception occurred, proceed with the rest of the function
            mockRespondProjectStatusMessage = RespondProjectStatusMessage()
            logging.debug(f"Emmiting '{type(mockRespondProjectStatusMessage).__name__}' event.")

            # Emit event to respond to a project status message.
            super().on_next(mockRespondProjectStatusMessage)

    def __scan_jira_projects():
        pass
