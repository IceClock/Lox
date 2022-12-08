from runTimeError import *


class Lox_instance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
        # self.fields = [] # change this to dict {} or something else if it doesnt work

    def get(self, name):
        if name.lexeme in self.fields.keys():
            return self.fields.get(name.lexeme)
        method = self.klass.find_method(name.lexeme)
        if method:
            # return method
            return method.bind(self)
        raise RunTimeError(name, "Undefined property '" + name.lexeme + "'.")

    def set(self, name, value):
        self.fields[name.lexeme] = value


    def __str__(self) -> str:
        return self.klass.name + " instance"