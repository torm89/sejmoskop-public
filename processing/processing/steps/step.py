from abc import ABC, abstractmethod


class Step(ABC):

    @classmethod
    @abstractmethod
    def run(cls, payload, *args, **kwargs):
        raise NotImplementedError
