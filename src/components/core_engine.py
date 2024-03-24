import logging

from common.interfaces import CoreEngineInterface

class CoreEngine(CoreEngineInterface):
    def __init__(self):
        super().__init__()

    def process_message(self, message):
        self.update(message)

    def update(self, message):
        logging.info(message)