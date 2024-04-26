from diagrams import Diagram, Cluster
from diagrams.programming.language import Python
from diagrams.custom import Custom

with Diagram(name="Signal System Architecture", 
             show=False, 
             direction="TB",
             outformat="png", 
             filename="assets/diagrams/signal_system_architecture") as diagram:
    
    users: Custom = Custom("Users", "../icons/users.png")

    with Cluster("Signal Application") as app_cluster:
        with Cluster("Assistant") as assistant_cluster:
            assistant: Python = Python("Assistant")
            slack: Custom = Custom("Slack", "../icons/slack.png")
        
        with Cluster("PM") as pm_cluster:
            pm: Python = Python("PM")
            github: Custom = Custom("Github", "../icons/github.png")

        users >> assistant

        assistant >> slack

        pm >> github

        assistant >> pm
        pm >> assistant
