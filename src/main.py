import logging

from mocks.slack_integration import MockSlackIntegration
from components.core_engine import CoreEngine

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    slack_integration = MockSlackIntegration()
    core_engine = CoreEngine()

    slack_integration.register_observer(core_engine)

    slack_integration.message_received("hello world!!")

if __name__ == "__main__":
    main()
