from abc import ABC, abstractmethod
from common.observer import Observable, Observer

class SlackIntegrationInterface(Observable, ABC):
    @abstractmethod
    def send_message(self, channel_id, message):
        """
        Sends a message to a specified channel.

        :param channel_id: The ID of the channel where the message will be sent.
        :param message: The message to send.
        """
        pass

    @abstractmethod
    def fetch_messages(self, channel_id, count=20):
        """
        Fetches a specified number of recent messages from a channel.

        :param channel_id: The ID of the channel from which messages will be fetched.
        :param count: The number of messages to fetch.
        :return: A list of messages.
        """
        pass

    @abstractmethod
    def create_channel(self, name, is_private=False):
        """
        Creates a new channel.

        :param name: The name of the channel.
        :param is_private: Indicates whether the channel is private.
        :return: The ID of the created channel.
        """
        pass

class CoreEngineInterface(Observer, ABC):
    @abstractmethod
    def process_message(self, message):
        pass