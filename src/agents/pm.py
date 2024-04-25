import logging
import os
import trio

from . import Agent, RAG, Scanner, VectorDB
from typing import List
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from events.project_status_message import IdentifiedProjectStatusMessageEvent, RespondProjectStatusMessageEvent, ProjectStatusQueryItem

def _new_config_dataset() -> List[ProjectStatusQueryItem]:
    return [
        ProjectStatusQueryItem(question="What is the current phase of the project and what are the key activities currently being undertaken?",
                               purpose="To gather detailed current status of the project to address the query in the message."),
        # ProjectStatusQueryItem(question="What milestones have recently been achieved in the project?",
        #                        purpose="To provide an update on recent successes and deliverables."),
        # ProjectStatusQueryItem(question="Are there any immediate challenges or risks facing the project that could impact progress?",
        #                        purpose="To identify potential issues or delays that need to be communicated."),
        # ProjectStatusQueryItem(question="What are the upcoming goals and deadlines for the project in the next quarter?",
        #                        purpose="To outline future objectives and timelines for better planning and expectation setting."),
        # ProjectStatusQueryItem(question="Can you provide any feedback from stakeholders or clients on the progress or impact of the project?",
        #                        purpose="To reflect stakeholder satisfaction and incorporate their feedback into project strategies."),
        # ProjectStatusQueryItem(question="What additional resources or support could potentially accelerate the progress of project?",
        #                        purpose="To identify needs that could speed up project completion or improve outcomes."),
        # ProjectStatusQueryItem(question="What is the current count of open, closed, and in-progress stories, issues, and bugs in the project?",
        #                        purpose="To obtain a quantitative snapshot of project activity and issue resolution efficiency, which helps in understanding workflow dynamics and potential bottlenecks."),
        # ProjectStatusQueryItem(question="How have the number of issues and bugs evolved over the past quarter?",
        #                        purpose="To track trends in project challenges and resolutions, providing insights into the development team's responsiveness and issue management effectiveness."),
        # ProjectStatusQueryItem(question="What percentage of the project's total tasks are currently in progress compared to those planned?",
        #                        purpose="To assess the project's progress against its planned milestones and timelines, helping to identify if the project is on track, ahead, or lagging."),
        # ProjectStatusQueryItem(question="Can you detail the cycle time for tasks from start to completion?",
        #                        purpose="To evaluate the efficiency of the project's workflow by analyzing the average time taken to complete tasks, which can highlight efficiency gains or needs for process optimization.")
    ]

class PM(Agent, RAG, Scanner):
    def __init__(self, vector_db: VectorDB):
        os.environ["GITHUB_APP_ID"] = os.getenv("APP_ID")
        os.environ["GITHUB_APP_PRIVATE_KEY"] = os.getenv("APP_PRIVATE_KEY")
        os.environ["GITHUB_BRANCH"] = "bot-branch"
        os.environ["GITHUB_BASE_BRANCH"] = "main"
        tools = GitHubToolkit.from_github_api_wrapper(GitHubAPIWrapper()).get_tools()
        Agent.__init__(self, tools, legacy=True)
        RAG.__init__(self, vector_db)
        Scanner.__init__(self)

    def _handle_event(self, event):
        super()._handle_event(event)
        if isinstance(event, IdentifiedProjectStatusMessageEvent):
            trio.run(self._handle_identified_project_status_message_event, event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    async def _handle_identified_project_status_message_event(self, event: IdentifiedProjectStatusMessageEvent):    
        pass
    
    async def _scan(self):
        project = "Signal"
        dataset = _new_config_dataset()
        async with trio.open_nursery() as nursery:
            for query_item in dataset:
                nursery.start_soon(self._process_query_item, project, query_item)
        self._add_documents([item.to_document() for item in dataset])
        # self._emit_event(RespondProjectStatusMessageEvent(**event.model_dump(), dataset=dataset))

    async def _process_query_item(self, project: str, query_item: ProjectStatusQueryItem):
        try:
            input = {"project": project, **query_item.model_dump()}
            output = await trio.to_thread.run_sync(
                lambda: self._invoke_prompt(prompt="znas/answer_project_status_message_question", input=input)
            )
            query_item.answer = output["output"]
        except Exception as e:
            logging.error(f"Error processing query item: {query_item.question}. Error: {e}")
            
    def online(self, scanner_interval_seconds=300):
        Scanner._start(self, scanner_interval_seconds)