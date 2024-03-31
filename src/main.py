import logging

from components.web_hooks_server import WebhooksServer
from components.slack_integration import SlackIntegration
from components.ai_agent import AIAgent

def main():
    # Configure logging.
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Starting webhooks HTTP server.
    WebhooksServer().start()

if __name__ == "__main__":
    main()
