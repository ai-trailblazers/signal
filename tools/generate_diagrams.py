from diagrams import Diagram, Cluster
from diagrams.programming.language import Python
from diagrams.custom import Custom

with Diagram(name="Signal System Architecture", 
             show=False, 
             direction="TB",
             outformat="png", 
             filename="docs/diagrams/signal_system_architecture") as diagram:
    
    user: Custom = Custom("User", "../icons/user.png")
    slack: Custom = Custom("Slack", "../icons/slack.png")
    jira: Custom = Custom("Jira", "../icons/jira.png")

    with Cluster("Signal Application") as app_cluster:
        with Cluster("AI Engine") as ai_cluster:
            ai_engine: Python = Python("AI Engine")

        with Cluster("Integrations") as integration_cluster:
            slack_integration: Python = Python("Slack Integration")
            jira_integration: Python = Python("Jira Integration")

        orchestrator: Python = Python("Orchestrator")

    user >> slack >> slack_integration >> orchestrator
    orchestrator >> ai_engine
    orchestrator >> jira_integration >> jira
    ai_engine >> orchestrator
