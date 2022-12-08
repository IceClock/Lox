from callable import *
from lox_instance import *

class Lox_class(Callable):
    def __init__(self, name, super_class, methods):
        self.name = name
        self.super_class = super_class
        self.methods = methods

    def find_method(self, name):
        if name in self.methods.keys():
            return self.methods.get(name)
        if self.super_class is not None:
            return self.super_class.find_method(name)
        return None

    def __str__(self) -> str:
        return self.name

    def call(self, interpreter, arguments):
        instance = Lox_instance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self):
        # return 0
        initializer = self.find_method("init")
        if not initializer:
            return 0
        return initializer.arity()