from abc import ABC, abstractmethod
from token import *
from typing import List, Optional
from expr import *

class Stmt_visitor:
    def __str__(self) -> str:
        return self.__class__.__name__

    def visit(self, stmt: "Stmt"):
        return self

class Stmt:
    def accept(self, visitor: Stmt_visitor):
        return visitor.visit(self)

class Expression(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor) -> str:
        return visitor.visit_expression_stmt(self)

class Print(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor) -> str:
        return visitor.visit_print_stmt(self)

class Var(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor) -> str:
        return visitor.visit_var_stmt(self)

class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor) -> str:
        return visitor.visit_block_stmt(self)

class If(Stmt):
    def __init__(self, condition, then_branch: Stmt, else_branch: Stmt):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor) -> str:
        return visitor.visit_if_stmt(self)

class Function(Stmt):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor) -> str:
        return visitor.visit_function_stmt(self)

class Return(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor) -> str:
        return visitor.visit_return_stmt(self)

class While(Stmt):
    def __init__(self, condition, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor) -> str:
        return visitor.visit_while_stmt(self)

class Break(Stmt):
    def __init__(self):
        pass

    def accept(self, visitor) -> str:
        return visitor.visit_break_stmt(self)

class Class(Stmt):
    def __init__(self, name, super_class: Optional[Variable],methods): # come back to this super class type
        self.name = name
        self.super_class = super_class
        self.methods = methods
    
    def accept(self, visitor)-> str:
        return visitor.visit_class_stmt(self)

