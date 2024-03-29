from abc import ABC, abstractmethod
from token import *
from stmt import * 
from expr import * 


class Visitor(ABC):
    @abstractmethod
    def visit_assign_expr(self,expr:Assign) -> str:
        pass

    @abstractmethod
    def visit_binary_expr(self,expr:Binary) -> str:
        pass

    @abstractmethod
    def visit_conditional_expr(self,expr:Conditional) -> str:
        pass

    @abstractmethod
    def visit_grouping_expr(self,expr:Grouping) -> str:
        pass

    @abstractmethod
    def visit_literal_expr(self,expr:Literal) -> str:
        pass

    @abstractmethod
    def visit_logical_expr(self,expr:Logical) -> str:
        pass

    @abstractmethod
    def visit_unary_expr(self,expr:Unary) -> str:
        pass

    @abstractmethod
    def visit_variable_expr(self,expr:Variable) -> str:
        pass

    @abstractmethod
    def visit_function_expr(self,expr:Function) -> str:
        pass

    @abstractmethod
    def visit_call_expr(self,expr:Call) -> str:
        pass

    @abstractmethod
    def visit_expression_stmt(self,stmt:Expression) -> str:
        pass

    @abstractmethod
    def visit_print_stmt(self,stmt:Print) -> str:
        pass

    @abstractmethod
    def visit_var_stmt(self,stmt:Var) -> str:
        pass

    @abstractmethod
    def visit_block_stmt(self,stmt:Block) -> str:
        pass

    @abstractmethod
    def visit_if_stmt(self,stmt:If) -> str:
        pass

    @abstractmethod
    def visit_function_stmt(self,stmt:Function) -> str:
        pass

    @abstractmethod
    def visit_return_stmt(self,stmt:Return) -> str:
        pass

    @abstractmethod
    def visit_while_stmt(self,stmt:While) -> str:
        pass

    @abstractmethod
    def visit_break_stmt(self,stmt:Break) -> str:
        pass

    @abstractmethod
    def visit_get_expr(self, expr: Expr)->str:
        pass
    
    @abstractmethod
    def visit_set_expr(self, expr: Expr)->str:
        pass

    @abstractmethod
    def visit_this_expr(self, expr: Expr)->str:
        pass

    @abstractmethod
    def visit_super_expr(self, expr: Super)->str:
        pass

    @abstractmethod
    def visit_class_stmt(self, stmt: Class)->str:
        pass