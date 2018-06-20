from abc import ABC, abstractmethod
from threading import Thread

from scrapt.utils import WaitUntil

__all__ = [
    'ArchiveFeed'
]


class Feed:
    def __init__(self):
        self._collection = []
        self._thread = None

    def collect(self):
        raise NotImplementedError

    def get_all(self, wait=False):
        if not wait:
            return self._collection
        if WaitUntil(lambda x: not x)(self._thread.is_alive):
            return self._collection
        else:
            return None

    def collection(self):
        """
        Generates next status
        :return: Generator of status
        """
        i = 0
        satisfies = WaitUntil(lambda x, y: len(x) > i or not y())
        while satisfies(self._collection, self._thread.is_alive):
            if len(self._collection) > i:
                i += 1
                yield self._collection[i - 1]
            else:
                break

    def start(self):
        self._thread = Thread(target=self.collect)
        self._thread.start()


class ArchiveFeed(ABC, Feed):
    def __init__(self):
        super(ArchiveFeed, self).__init__()

    def collect(self):
        raise NotImplementedError


class StreamFeed(ABC, Feed):
    def __init__(self):
        super(StreamFeed, self).__init__()

    def collect(self):
        return self.stream()

    @abstractmethod
    def stream(self):
        raise NotImplementedError
