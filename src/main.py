import logging
import signal
import sys

from components.slack import Slack
from components.jira import Jira

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Application is running. Press Ctrl+C to exit.")
    
    slack = Slack()
    jira = Jira()

    slack.subscribe(jira)
    slack.start(60)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)    
    signal.pause()
    
    slack.stop()
    jira.dispose()

def signal_handler(*_):
    sys.exit(0)

if __name__ == "__main__":
    main()
