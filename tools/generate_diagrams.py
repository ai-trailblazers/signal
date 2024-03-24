from diagrams import Diagram, Cluster
from diagrams.programming.language import Python
from diagrams.custom import Custom

with Diagram(name="Signal System Architecture", 
             show=False, 
             direction="TB",
             outformat="png", 
             filename="docs/diagrams/signal_system_architecture") as diagram:
    
    users: Custom = Custom("Users", "../icons/users.png")
    slack: Custom = Custom("Slack", "../icons/slack.png")
    jira: Custom = Custom("Jira", "../icons/jira.png")

    with Cluster("Signal Application") as app_cluster:
        with Cluster("Core Engine") as core_engine_cluster:
            core_engine: Python = Python("Core Engine")
        
        with Cluster("Slack Integration Module") as slack_integration_cluster:
            slack_integration: Python = Python("Slack Integration")
        
        with Cluster("Jira Integration Module") as jira_integration_cluster:
            jira_integration: Python = Python("Jira Integration")

        with Cluster("RAG Integration Module") as rag_integration_cluster:
            rag_integration: Python = Python("RAG Integration")
        
        with Cluster("AI Agent") as ai_agent_cluster:
            ai_agent: Python = Python("AI Agent")

        users >> slack >> slack_integration >> core_engine
        core_engine >> ai_agent
        core_engine >> jira_integration >> jira
        core_engine >> rag_integration
        ai_agent >> slack_integration
