import logging

from . import Agent
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage

class Jira(Agent):
    def __init__(self):
        super().__init__()

    def _handle_event(self, event):
        super()._handle_event(event)

        if isinstance(event, IdentifiedProjectStatusMessage):
            self._handle_identified_project_status_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    def _handle_identified_project_status_message_event(self, event: IdentifiedProjectStatusMessage):
        result = self._invoke_prompt(prompt="znas/process_project_status_message",
                                     input=event.content["input"],
                                     author=event.content["author"])
        content = {
            "input": result["output"],
            "placeholder": "just a placeholder for now"
        }

        self._emmit_event(RespondProjectStatusMessage(content=content))
