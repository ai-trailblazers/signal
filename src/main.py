import logging

from components.web_hooks_server import WebHooksServer
from components.slack_integration import SlackIntegration


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    webHookServer = WebHooksServer()
    slackIntegration = SlackIntegration()

    subscriber = webHookServer.start()

    subscriber.subscribe(slackIntegration)

    webHookServer.http_request_received("this is a message from Slack")

if __name__ == "__main__":
    main()
