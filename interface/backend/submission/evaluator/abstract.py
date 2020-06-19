from abc import ABC, abstractmethod


class Evaluator(ABC):
    @abstractmethod
    def evaluate(submission):
        pass

    @abstractmethod
    def update(submission):
        pass
