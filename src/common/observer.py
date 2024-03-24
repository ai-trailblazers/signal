from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, message):
        """
        Receives update with a message.

        :param message: The message to be processed.
        """
        pass

class Observable(ABC):
    def __init__(self):
        self.observers = []

    def register_observer(self, observer: Observer):
        """
        Registers an observer to the observable object.

        :param observer: The observer to be registered.
        """
        self.observers.append(observer)

    def unregister_observer(self, observer: Observer):
        """
        Unregisters an observer from the observable object.

        :param observer: The observer to be unregistered.
        """
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self, message):
        """
        Notifies all registered observers with the given message.

        :param message: The message to be sent to observers.
        """
        for observer in self.observers:
            observer.update(message)
