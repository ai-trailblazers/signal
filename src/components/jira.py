import logging

from . import Agent
from typing import cast
from reactivex import Subject
from langchain import hub
from langchain.agents import AgentType, initialize_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper

from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage

class Jira(Subject, Agent):
    def __init__(self):
        super().__init__()

    def _create_agent(self):
        if self.agent:
            return
        
        all_tools = JiraToolkit.from_jira_api_wrapper(JiraAPIWrapper()).get_tools()
        exclude_tools = ["create_issue", "create_page"]
        tools = [tool for tool in all_tools if tool.mode not in exclude_tools]
        self.agent = initialize_agent(tools=tools,
                                      llm=ChatOpenAI(model="gpt-4-0125-preview", temperature=0),
                                      agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                      verbose=True,
                                      handle_parsing_errors=True)

    def on_next(self, event):
        if isinstance(event, IdentifiedProjectStatusMessage):
            self._handle_identified_project_status_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    def on_error(self, error):
        logging.error(error)

    def _handle_identified_project_status_message_event(self, event: IdentifiedProjectStatusMessage):
        logging.debug(f"Handling '{type(event).__name__}' event.")
        
        prompt = cast(PromptTemplate, hub.pull("znas/process_project_status_message"))
        content = None

        with self.lock:
            # build retry logic
            try:
                result = self.agent.invoke(prompt.format(input=event.content["input"],
                                                         _from=event.content["_from"]))
                content = {
                    "input": result["output"],
                    "placeholder": "just a placeholder for now"
                }
            except Exception as e:
                logging.error(f"An error occurred while invoking the chain: {e}")
                return
        
        assert content, "The variable 'content' should not be empty or None"

        respondProjectStatusMessage = RespondProjectStatusMessage(content=content)

        logging.debug(f"Emmiting '{type(respondProjectStatusMessage).__name__}' event.")

        # Emit event to respond to a project status message.
        super().on_next(respondProjectStatusMessage)
