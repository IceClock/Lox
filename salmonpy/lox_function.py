from callable import *
from environment import *
from stmt import *
from runTimeError import *
from lox_instance import *

class Lox_function(Callable):
    declaration: Function
    closure: Environment
    is_initializer: bool

    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool):
        self.closure = closure
        self.declaration = declaration
        self.is_initializer = is_initializer

    def bind(self,instance: Lox_instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return Lox_function(self.declaration, environment, self.is_initializer)

    def call(self,interpreter, arguments):
        # environment = Environment(interpreter.globals)
        environment = Environment(self.closure)
        for i in range(0,len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme,arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return_exception as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def arity(self):
        return len(self.declaration.params)

    def __str__(self) -> str:
        return "<fn " + self.declaration.name.lexeme + ">"

