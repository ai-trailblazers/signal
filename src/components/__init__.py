import logging

from abc import ABC, abstractmethod
from typing import Dict, Any
from reactivex import Subject
from langchain import hub
from langchain.agents import AgentExecutor, AgentType, create_tool_calling_agent, initialize_agent
from langchain_openai import ChatOpenAI

OPEN_AI_MODEL="gpt-4-0125-preview"

class Agent(Subject, ABC):
    def __init__(self, legacy: bool, tools):
        super().__init__()
        self.legacy = legacy
        self.tools = tools

    @abstractmethod
    def _handle_event(self, event):
        logging.debug(f"Handling '{type(event).__name__}' event.")

    def _get_agent_executor(self, prompt) -> AgentExecutor:
        if self.legacy:
            agent = initialize_agent(llm=ChatOpenAI(temperature=0.1),
                tools=self.tools,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True)
            return prompt | agent
        else:
            agent=create_tool_calling_agent(llm=ChatOpenAI(model=OPEN_AI_MODEL, temperature=0),
                                            prompt=prompt,
                                            tools=self.tools)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def _invoke_prompt(self, prompt: str, input: Dict[str, Any], tools) -> Dict[str, Any]:
        num_tries = 5
        attempts = 0
        while attempts < num_tries:
            with self.lock:
                try:
                    if self.legacy:
                        pass
                    else:
                        return self._get_agent_executor(prompt=hub.pull(prompt)).invoke(input=input)
                except Exception as e:
                    attempts += 1
                    if attempts >= num_tries:
                        logging.error(f"Failed to invoke prompt after {num_tries} attempts: {e}")
                        raise
                    else:
                        logging.warning(f"Attempt {attempts} failed, retrying: {e}")
        return None
    
    def _emmit_event(self, event):
        logging.debug(f"Emmiting '{type(event).__name__}' event.")
        super().on_next(event)

    def on_next(self, event):
        try:
            self._handle_event(event)
        except Exception as e:
            logging.error(f"There was an error handling event '{type(event).__name__}'. Error: {e}")

    def on_error(self, error):
        logging.error(error)
