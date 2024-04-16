import logging

from abc import ABC, abstractmethod
from threading import Lock
from typing import cast, Dict, Any
from langchain import hub
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate

class Agent(ABC):
    def __init__(self):
        super().__init__()
        self.agent: AgentExecutor = None
        self.lock = Lock()
        self._create_agent()

    @abstractmethod
    def _create_agent(self):
        pass

    def _invoke_prompt(self, prompt: str, num_tries: int = 5, **kwargs: Any) -> Dict[str, Any]:
        attempts = 0
        while attempts < num_tries:
            with self.lock:
                try:
                    prompt = cast(PromptTemplate, hub.pull(prompt))
                    return self.agent.invoke(prompt.format(**kwargs))
                except Exception as e:
                    attempts += 1
                    if attempts >= num_tries:
                        logging.error(f"Failed to invoke prompt after {num_tries} attempts: {e}")
                        raise
                    else:
                        logging.warning(f"Attempt {attempts} failed, retrying: {e}")
        return None