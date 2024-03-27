# from abc import abstractmethod, ABC
# from common.observer import Observable, Observer

# class Message(ABC):
#     def handle(self, observer: Observer):
#         observer.handle_message(self)

# class HttpServer(Observable, ABC):
#     @abstractmethod
#     def start(self):
#         pass

# class SlackIntegration(Observer, Observable, ABC):
#     def update(self, message: Message):
#         message.handle(self)
