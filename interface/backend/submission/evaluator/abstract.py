from abc import ABC, abstractmethod


class Evaluator(ABC):
    @staticmethod
    @abstractmethod
    def evaluate(submission):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def update(submission):
        raise NotImplementedError()
