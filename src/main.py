import logging

from components.slack import Slack
from components.github import Github

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Application is running. Press Ctrl+C to exit.")
    
    slack = Slack()
    github = Github()

    slack.subscribe(github)
    github.subscribe(slack)
    slack.start()
    
    slack.dispose()
    github.dispose()

if __name__ == "__main__":
    main()
