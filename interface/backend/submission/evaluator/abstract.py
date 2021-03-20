from abc import ABC, abstractmethod


class Evaluator(ABC):
    @staticmethod
    @abstractmethod
    def evaluate(submission):
        raise NotImplemented()

    @staticmethod
    @abstractmethod
    def update(submission):
        raise NotImplemented()
