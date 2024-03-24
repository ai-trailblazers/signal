from unittest.mock import Mock
from common.interfaces import SlackIntegrationInterface

class MockSlackIntegration(SlackIntegrationInterface):
    def __init__(self):
        super().__init__()
        
        # Initialize the mock methods directly in the method definitions
        self.send_message = Mock(name="send_message")
        self.fetch_messages = Mock(name="fetch_messages", return_value=[])
        self.create_channel = Mock(name="create_channel", return_value="mock_channel_id")
    
    def send_message(self, channel_id, message):
        return self.send_message(channel_id, message)

    def fetch_messages(self, channel_id, count=20):
        return self.fetch_messages(channel_id, count)

    def create_channel(self, name, is_private=False):
        return self.create_channel(name, is_private)

    def message_received(self, message):
        self.notify_observers(message=message)
