import logging
import threading
import json

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List
from reactivex import Subject
from faiss import IndexFlatL2
from langchain import hub
from langchain_core.documents import Document
from langchain.agents import AgentExecutor, AgentType, initialize_agent, create_tool_calling_agent
from langchain_community.vectorstores.faiss import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore

OPEN_AI_MODEL = "gpt-4-0125-preview"

class Agent(Subject, ABC):
    def __init__(self, tools, legacy: bool):
        super().__init__()
        self.tools = tools
        self.legacy = legacy

    @abstractmethod
    def _handle_event(self, event):
        logging.debug(f"Handling '{type(event).__name__}' event.")

    def _get_agent_executor(self, prompt_template):
        if self.legacy:
            legacy_agent = initialize_agent(llm=ChatOpenAI(model=OPEN_AI_MODEL, temperature=0),
                                                 tools=self.tools,
                                                 agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                                 verbose=True,
                                                 handle_parsing_errors=True)
            class LegacyExecutor:
                def __init__(self, agent, prompt_template):
                    self.agent = agent
                    self.prompt_template = prompt_template

                def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
                    prompt = self.prompt_template.format(**input)
                    return self.agent.invoke(input=prompt)
            return LegacyExecutor(legacy_agent, prompt_template)
        agent = create_tool_calling_agent(llm=ChatOpenAI(model=OPEN_AI_MODEL, temperature=0),
                                          prompt=prompt_template,
                                          tools=self.tools)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def _retry_operation(self, func: Callable, *args, **kwargs) -> Any:
        num_tries = 5
        attempts = 0
        while attempts < num_tries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempts += 1
                if attempts >= num_tries:
                    logging.error(f"Failed after {num_tries} attempts: {e}")
                    raise
                else:
                    logging.warning(f"Attempt {attempts} failed, retrying: {e}")     

    def _invoke_prompt(self, prompt: str, input: Dict[str, Any]) -> Dict[str, Any]:
        if 'agent_scratchpad' not in input:
            input['agent_scratchpad'] = []
        if 'chat_history' not in input:
            input['chat_history'] = []
        executor = self._get_agent_executor(hub.pull(prompt))
        return self._retry_operation(executor.invoke, input)
    
    def _run_chain(self, prompt: str, input: Dict[str, Any]) -> Dict[str, Any]:
        chain = hub.pull(prompt) | ChatOpenAI(model=OPEN_AI_MODEL, temperature=0)
        return chain.invoke(input)

    def _emit_event(self, event, is_local_event=False):
        logging.debug(f"Emitting '{type(event).__name__}' event.")
        on_next_func = super().on_next
        def f():
            if is_local_event:
                self._handle_event(event)
            else:
                on_next_func(event)
        threading.Thread(target=f).start()

    def on_next(self, event):
        try:
            self._handle_event(event)
        except Exception as e:
            logging.error(f"There was an error handling event '{type(event).__name__}'. Error: {e}")

    def on_error(self, error):
        logging.error(error)

class RAG:
    def __init__(self, index: str):
        self._lock = threading.Lock()
        self._index = index
        self._embeddings = OpenAIEmbeddings()
        self._vector_store = FAISS(
            embedding_function=self._embeddings,
            index=IndexFlatL2(1536),
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

    def _create_combined_embedding(self, document: Document):
        content_embedding = self._embeddings.embed_documents([document.page_content])[0]
        metadata_embedding = self._embeddings.embed_documents([json.dumps(document.metadata)])[0]
        # Combine embeddings using averaging
        return (content_embedding + metadata_embedding) / 2

    def _add_documents(self, documents: List[Document]):
        embeddings = [self._create_combined_embedding(document) for document in documents]
        with self._lock:
            self._vector_store.add_documents(embeddings)
