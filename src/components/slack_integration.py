from messages.slack_event_message import SlackEventMessage
from reactivex import Observer

class SlackIntegration(Observer):
    def on_next(self, message: SlackEventMessage):
        print(f"Received message: {message.msg}")

    def on_error(self, error):
        print(f"Error: {error}")

    def on_completed(self):
        print("Completed")
