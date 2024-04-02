import logging

from components.web_hooks_server import WebhooksServer
from components.slack import Slack
from components.jira import Jira

def main():
    # Configure logging.
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Starting webhooks HTTP server.
    # WebhooksServer().start()

    slack = Slack()
    jira = Jira()

    with slack.subscribe(jira):
        slack.scanMessages()

if __name__ == "__main__":
    main()
