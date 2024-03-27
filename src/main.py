import logging

from components.slack_integration import SlackIntegration
from components.slack_web_hooks import SlackWebHooksServer
from messages.slack_event_message import SlackEventMessage
from messages.web_hook_message import WebHookMessage

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    http_server = SlackWebHooksServer()
    slack_integration = SlackIntegration()

    http_server.register_observer(slack_integration)

    msg = SlackEventMessage()

    http_server.notify_observers(msg)

    tw = WebHookMessage()

    http_server.notify_observers(tw)

if __name__ == "__main__":
    main()
