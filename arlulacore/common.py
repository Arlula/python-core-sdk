import abc
import json

class ArlulaObject(abc.ABC):
    def __repr__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])[1:-1].replace('\'', '')

    @abc.abstractmethod
    def dict(self):
        pass

    def format(self, format: str) -> str:
        if format == "json":
            return json.dumps(self.dict())
        if format == "text":
            return str(self)
        if format == "pretty-json":
            return json.dumps(self.dict(), indent=1)
        if format == "table":
            return str(self)
