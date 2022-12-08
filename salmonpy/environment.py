from runTimeError import *

class Environment:
    # def __init__(self, enclosing: Optional["Environment"] = None):
    def __init__(self, enclosing = None):
        self.enclosing = enclosing
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def ancestor(self, distance)-> "Environment": ## double check this one if it doesnt work
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

    def get_at(self, distance, name):
        return self.ancestor(distance).values.get(name)
        # return None

    def assign_at(self, distance, name, value):
        self.ancestor(distance).values[name.lexeme] = value ## check this if it doesnt work

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise RunTimeError(name, "Undefined variable '" + name.lexeme + "'.")

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return # this is what i was missing that didint make the "counter" test work well.
        raise RunTimeError(name,"Undefined variable '" + name.lexeme + "'.")
