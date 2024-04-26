import logging
import os
import trio

from . import Agent, RAG, Scanner, VectorDB, SetMemory, new_project_query_items, generate_context_from_documents
from typing import List
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_core.documents import Document
from events import Message
from events.project_status_message import IdentifiedProjectStatusMessageEvent, ProjectStatusQueryItem, RespondProjectStatusMessageEvent

class PM(Agent, RAG, Scanner):
    def __init__(self, vector_db: VectorDB, set_memory: SetMemory):
        os.environ["GITHUB_APP_ID"] = os.getenv("APP_ID")
        os.environ["GITHUB_APP_PRIVATE_KEY"] = os.getenv("APP_PRIVATE_KEY")
        os.environ["GITHUB_BRANCH"] = "bot-branch"
        os.environ["GITHUB_BASE_BRANCH"] = "main"
        tools = GitHubToolkit.from_github_api_wrapper(GitHubAPIWrapper()).get_tools()
        Agent.__init__(self, tools, legacy=True)
        RAG.__init__(self, vector_db)
        Scanner.__init__(self)
        self.set_memory = set_memory

    def _handle_event(self, event):
        super()._handle_event(event)
        if isinstance(event, IdentifiedProjectStatusMessageEvent):
            trio.run(self._handle_identified_project_status_message_event, event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    def _generate_memory_id(self, index: str):
        return f"pm:{index}"
    
    def _is_message_processed(self, message: Message) -> bool:
        return self.set_memory.does_memory_exist(self._generate_memory_id(message.client_msg_id))

    async def _handle_identified_project_status_message_event(self, event: IdentifiedProjectStatusMessageEvent):
        try:    
            if self._is_message_processed(event):
                return
            # VectorDB search.
            context = generate_context_from_documents(self._search(event.text))
            if not context:
                logging.warning(f"Did not find documents related to message '{event.text}'")
                return
            self._emit_event(RespondProjectStatusMessageEvent(**event.model_dump(), context=context))
        except Exception as e:
            logging.error(f"Error handling project status message: {e}")

    async def _scan(self):
        project = "Signal"
        query_items = new_project_query_items()
        async with trio.open_nursery() as nursery:
            for query_item in query_items:
                nursery.start_soon(self._process_query_item, project, query_item)
        self._add_documents([item.to_document() for item in query_items])

    async def _process_query_item(self, project: str, query_item: ProjectStatusQueryItem):
        try:
            input = {"project": project, **query_item.model_dump()}
            output = await trio.to_thread.run_sync(
                lambda: self._invoke_prompt(prompt="znas/answer_project_status_message_question", input=input)
            )
            query_item.answer = output["output"]
        except Exception as e:
            logging.error(f"Error processing query item: {query_item.question}. Error: {e}")
            
    def online(self, initial_wait_seconds=0, scanner_interval_seconds=60):
        self._start(initial_wait_seconds, scanner_interval_seconds)
