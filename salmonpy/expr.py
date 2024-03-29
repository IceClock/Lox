from abc import ABC, abstractmethod
from token import Token
from typing import List 


class Expr_visitor:
    def __str__(self):
        return self.__class__.__name__

    def visit(self, expr: "Expr"):
        return self
  
class Expr:
    def accept(self, visitor: Expr_visitor):
        return visitor.visit(self)
    # def accept(self, visitor):
    #     return visitor.visit(self)

class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor) -> str:
        return visitor.visit_assign_expr(self)

class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr
    
    def __init__(self, left: Expr, operator: Token,  right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_binary_expr(self)

class Conditional(Expr):
    def __init__(self, condition: Expr, left: Expr, right: Expr):
        self.condition = condition
        self.left = left
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_conditional_expr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor) -> str:
        return visitor.visit_grouping_expr(self)

class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor) -> str:
        return visitor.visit_literal_expr(self)

class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_logical_expr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_unary_expr(self)

class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor) -> str:
        return visitor.visit_variable_expr(self)

# class Function(Expr):
#     def __init__(self, params: list[Token], body):
#         self.params = params
#         self.body = body

#     def accept(self, visitor) -> str:
#         return visitor.visit_function_expr(self)

class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, args: list[Expr]):
        self.callee = callee
        self.paren = paren
        self.args = args

    def accept(self, visitor) -> str:
        return visitor.visit_call_expr(self)

class Get(Expr):
    def __init__(self, object: Expr, name: Token):
        self.object = object
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_get_expr(self)

class Set(Expr):
    def __init__(self, object: Expr, name: Token, value: Expr):
        self.object = object
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_set_expr(self)

class This(Expr):
    def __init__(self, keyword: Token):
        self.keyword = keyword

    def accept(self, visitor):
        return visitor.visit_this_expr(self)

class Super(Expr):
    def __init__(self, keyword: Token, method: Token):
        self.keyword = keyword
        self.method = method

    def accept(self, visitor):
        return visitor.visit_super_expr(self)
        
