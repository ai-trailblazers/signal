import logging

from components.web_hooks_server import WebHooksServer
from components.slack_integration import SlackIntegration
from components.ai_agent import AIAgent
from messages.web_hooks_server_message import WebHooksServerMessage, WebHooksServerMessageType

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    webHooksServer = WebHooksServer()
    slackIntegration = SlackIntegration()
    agent = AIAgent()

    webHooksServer.start().subscribe(slackIntegration)
    slackIntegration.start().subscribe(agent)

    webHookMessage = WebHooksServerMessage(WebHooksServerMessageType.SLACK, "znas@znas.io", "mock message from Slack")

    webHooksServer.http_request_received(webHookMessage)

if __name__ == "__main__":
    main()
