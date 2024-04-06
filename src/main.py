import logging
import signal
import sys

from components.web_hooks_server import WebhooksServer
from components.slack import Slack
from components.jira import Jira

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    slack = Slack()
    jira = Jira()

    with slack.subscribe(jira):
        slack.start(5)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        logging.info("Application is running. Press Ctrl+C to exit.")
        signal.pause()

def signal_handler(*_):
    sys.exit(0)

if __name__ == "__main__":
    main()
