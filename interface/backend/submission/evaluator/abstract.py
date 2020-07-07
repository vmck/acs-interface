from abc import ABC, abstractstaticmethod


class Evaluator(ABC):
    @abstractstaticmethod
    def evaluate(submission):
        pass

    @abstractstaticmethod
    def update(submission):
        pass
