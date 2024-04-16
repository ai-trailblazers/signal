import logging

from abc import ABC, abstractmethod
from threading import Lock
from typing import cast, Dict, Any
from reactivex import Subject
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

class Agent(Subject, ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def _handle_event(self, event):
        pass

    def _get_agent_executor(self, prompt) -> AgentExecutor:
        tools=[]
        llm=ChatOpenAI(model="gpt-4", temperature=0)
        agent=create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
        executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return executor

    def on_next(self, event):
        try:
            self._handle_event(event)
        except Exception as e:
            logging.error(f"There was an error handling event '{type(event).__name__}'. Error: {e}")

    def on_error(self, error):
        logging.error(error)

    def _invoke_prompt(self, prompt: str, input: Dict[str, Any]) -> Dict[str, Any]:
        num_tries = 5
        attempts = 0
        while attempts < num_tries:
            with self.lock:
                try:
                    # prompt = cast(PromptTemplate, p)
                    # r = prompt.format(**kwargs)
                    return self._get_agent_executor(hub.pull(prompt)).invoke(input=input)
                except Exception as e:
                    attempts += 1
                    if attempts >= num_tries:
                        logging.error(f"Failed to invoke prompt after {num_tries} attempts: {e}")
                        raise
                    else:
                        logging.warning(f"Attempt {attempts} failed, retrying: {e}")
        return None