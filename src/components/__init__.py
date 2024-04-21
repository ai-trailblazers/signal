import logging
import threading

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
        self.tools = tools

        if legacy:
            self.legacy_agent = initialize_agent(llm=ChatOpenAI(temperature=0),
                tools=self.tools,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True)

    @abstractmethod
    def _handle_event(self, event):
        logging.debug(f"Handling '{type(event).__name__}' event.")

    def _get_agent_executor(self, prompt_template):
        if self.legacy_agent:
            class LegacyExecutor:
                def __init__(self, agent, prompt_template):
                    self.agent = agent
                    self.prompt_template = prompt_template

                def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
                    if 'agent_scratchpad' not in input:
                        input['agent_scratchpad'] = ''

                    prompt = self.prompt_template.format(**input)
                    return self.agent.invoke(input=prompt)

            return LegacyExecutor(self.legacy_agent, prompt_template)
        else:
            agent=create_tool_calling_agent(llm=ChatOpenAI(model=OPEN_AI_MODEL, temperature=0),
                                            prompt=prompt_template,
                                            tools=self.tools)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def _invoke_prompt(self, prompt: str, input: Dict[str, Any]) -> Dict[str, Any]:
        num_tries = 5
        attempts = 0
        while attempts < num_tries:
            with self.lock:
                try:
                    return self._get_agent_executor(prompt_template=hub.pull(prompt)).invoke(input=input)
                except Exception as e:
                    attempts += 1
                    if attempts >= num_tries:
                        logging.error(f"Failed to invoke prompt after {num_tries} attempts: {e}")
                        raise
                    else:
                        logging.warning(f"Attempt {attempts} failed, retrying: {e}")
        return None
    
    def _emmit_event(self, event, is_local_event=False):
        logging.debug(f"Emmiting '{type(event).__name__}' event.")
        on_next = super().on_next
        def f():
            if is_local_event:
                self._handle_event(event)
            else:
                on_next(event)
        threading.Thread(target=f).start()

    def on_next(self, event):
        try:
            self._handle_event(event)
        except Exception as e:
            logging.error(f"There was an error handling event '{type(event).__name__}'. Error: {e}")

    def on_error(self, error):
        logging.error(error)
