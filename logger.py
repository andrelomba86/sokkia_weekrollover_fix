from typing import List


class Observer:
    def log(self, message):
        raise NotImplementedError(
            "The 'log' method must be implemented by the observer.")

    def debug(self, message):
        pass

    def error(self, message):
        pass


class Logger:
    def __init__(self):
        self._observers: List[Observer] = []

    def add_observer(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, message, *args, **kwargs):
        for observer in self._observers:
            observer.log(message)

    def debug(self, message, *args, **kwargs):
        for observer in self._observers:
            observer.debug(message)

    def error(self, message, *args, **kwargs):
        for observer in self._observers:
            observer.error(message)


logger = Logger()
