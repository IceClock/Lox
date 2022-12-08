from abc import ABC, abstractclassmethod

class Callable(ABC):
    # _arity: int = 0
    @abstractclassmethod
    def call(self, interpreter, arguments):
        pass

    @abstractclassmethod
    def arity(self)-> int:
        pass
        # return self._arity