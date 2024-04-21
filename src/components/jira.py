import logging

from . import Agent
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage

class Jira(Agent):
    def __init__(self):
        super().__init__(legacy=False, tools=[])

    def _handle_event(self, event):
        super()._handle_event(event)

        if isinstance(event, IdentifiedProjectStatusMessage):
            self._handle_identified_project_status_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    def _handle_identified_project_status_message_event(self, event: IdentifiedProjectStatusMessage):
        result = self._invoke_prompt(prompt="znas/process_project_status_message",
                                     input={"input": event.input, "author": event.author})

        self._emmit_event(RespondProjectStatusMessage(input=result["output"],
                                                      author=event.author))
