import time
from callable import *

class Clock(Callable):

    def __init__(self) -> None:
        super().__init__()

    def call(self,interpreter, arguments):
        return time.time()

    def arity(self):
        return 0

    def __str__(self) -> str:
        return "<native fn>"