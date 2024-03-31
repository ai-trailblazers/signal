import logging

from components.web_hooks_server import WebHooksServer
from components.slack_integration import SlackIntegration
from components.ai_agent import AIAgent

from events.web_hook import WebHookEvent, WebHookEventType

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    webHooksServer = WebHooksServer()
    slackIntegration = SlackIntegration()
    agent = AIAgent()

    webHooksServer.start().subscribe(slackIntegration)
    slackIntegration.start().subscribe(agent)

    webHookEvent = WebHookEvent(WebHookEventType.SLACK, "znas@znas.io", "mock event from web hooks server")

    webHooksServer.http_request_received(webHookEvent)

if __name__ == "__main__":
    main()
