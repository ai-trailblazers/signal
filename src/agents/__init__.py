import logging
import threading
import trio

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List
from reactivex import Subject
from faiss import IndexFlatL2
from events.project_status_message import ProjectStatusQueryItem
from langchain import hub
from langchain_core.documents import Document
from langchain.agents import AgentExecutor, AgentType, initialize_agent, create_tool_calling_agent
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore

OPEN_AI_MODEL = "gpt-4-0125-preview"

def new_project_query_items() -> List[ProjectStatusQueryItem]:
    return [
        ProjectStatusQueryItem(question="What is the current phase of the project and what are the key activities currently being undertaken?",
                               purpose="To gather detailed current status of the project to address the query in the message."),
        ProjectStatusQueryItem(question="What milestones have recently been achieved in the project?",
                               purpose="To provide an update on recent successes and deliverables."),
        ProjectStatusQueryItem(question="Are there any immediate challenges or risks facing the project that could impact progress?",
                               purpose="To identify potential issues or delays that need to be communicated."),
        ProjectStatusQueryItem(question="What are the upcoming goals and deadlines for the project in the next quarter?",
                               purpose="To outline future objectives and timelines for better planning and expectation setting."),
        ProjectStatusQueryItem(question="Can you provide any feedback from stakeholders or clients on the progress or impact of the project?",
                               purpose="To reflect stakeholder satisfaction and incorporate their feedback into project strategies."),
        ProjectStatusQueryItem(question="What additional resources or support could potentially accelerate the progress of project?",
                               purpose="To identify needs that could speed up project completion or improve outcomes."),
        ProjectStatusQueryItem(question="What is the current count of open, closed, and in-progress stories, issues, and bugs in the project?",
                               purpose="To obtain a quantitative snapshot of project activity and issue resolution efficiency, which helps in understanding workflow dynamics and potential bottlenecks."),
        ProjectStatusQueryItem(question="How have the number of issues and bugs evolved over the past quarter?",
                               purpose="To track trends in project challenges and resolutions, providing insights into the development team's responsiveness and issue management effectiveness."),
        ProjectStatusQueryItem(question="What percentage of the project's total tasks are currently in progress compared to those planned?",
                               purpose="To assess the project's progress against its planned milestones and timelines, helping to identify if the project is on track, ahead, or lagging."),
        ProjectStatusQueryItem(question="Can you detail the cycle time for tasks from start to completion?",
                               purpose="To evaluate the efficiency of the project's workflow by analyzing the average time taken to complete tasks, which can highlight efficiency gains or needs for process optimization.")
    ]

def generate_context_from_documents(documents: List[Document]) -> str:
    if len(documents) == 0:
        return None
    context_lines = [
        "## CONTEXT ##",
        *(
            f"Content: {item.page_content}"
            for item in documents
        ),
        "#############"
    ]
    return "\n".join(context_lines)

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
    
    def _run_chain(self, prompt: str, input: Dict[str, Any], temperature=1) -> Dict[str, Any]:
        chain = hub.pull(prompt) | ChatOpenAI(model=OPEN_AI_MODEL, temperature=temperature)
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
            logging.error(f"There was an error handling event '{type(event).__name__}': {e}")

    def on_error(self, error):
        logging.error(error)

class VectorDB:
    def __init__(self, index: str):
        self.index = index
        self.lock = threading.Lock()
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=IndexFlatL2(1536),
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

class RAG:
    def __init__(self, vector_db: VectorDB):
        self._vector_db = vector_db

    def _add_documents(self, documents: List[Document]):
        if not documents or len(documents) == 0:
            return
        with self._vector_db.lock:
            self._vector_db.vector_store.add_documents(documents)
            length = len(documents)
            if length == 1:
                logging.info(f"'{length}' document was added to the vector database.")
            else:
                logging.info(f"'{length}' documents were added to the vector database.")
            
    def _search(self, query: str, top_k: int = 100) -> List[Document]:
        try:
            with self._vector_db.lock:
                return self._vector_db.vector_store.search(query=query,
                                                           search_type='similarity',
                                                           top_k=top_k)
        except Exception as e:
            logging.error(f"Error performing semantic search: {e}")
        return []

class Scanner(ABC):
    def __init__(self):
        self._is_running = False
    
    @abstractmethod
    async def _scan(self):
        pass

    async def _periodic_task(self, initial_wait_seconds, interval_seconds):
        while True:
            if self._is_running:
                await trio.sleep(interval_seconds)
            try:
                self._is_running = True
                await trio.sleep(initial_wait_seconds)
                await self._scan()
            except Exception as e:
                logging.error(f"An error occurred scanning: {e}")

    def _start(self, initial_wait_seconds, interval_seconds):
        if initial_wait_seconds < 1:
            initial_wait_seconds = 1
        if self._is_running:
            logging.warn("Scanner is already running.")
            return
        async def start_periodic_scans():
            await self._periodic_task(initial_wait_seconds, interval_seconds)
        def run_in_thread():
            trio.run(start_periodic_scans)
        thread = threading.Thread(target=run_in_thread)
        thread.start()

class SetMemory:
    def __init__(self):
        self.memory = set()
        self.lock = threading.Lock()

    def does_memory_exist(self, index: str):
        with self.lock:
            return index in self.memory
        
    def add_memory(self, index: str):
        with self.lock:
            self.memory.add(index)
