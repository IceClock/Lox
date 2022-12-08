from expr import *
from stmt import *
from interpreter import *
from function_type import *
from class_type import *

class Resolver(Expr_visitor, Stmt_visitor):

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.error_handler = self.interpreter.error_handler
        self.scopes = []
        self.current_function = Function_type.NONE
        self.current_class = Class_type.NONE

    def resolve_all(self, statements):
        for stmt in statements:
            self.resolve(stmt)

    def visit_block_stmt(self, stmt: Block):
        self.begin_scope()
        self.resolve_all(stmt.statements)
        self.end_scope()
        # return None

    def visit_class_stmt(self, stmt: Class):
        enclosing_class = self.current_class
        self.current_class = Class_type.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)
        if stmt.super_class and (stmt.name.lexeme == stmt.super_class.name.lexeme):
            self.error_handler.token_error(stmt.super_class.name, "A class can't inherit from itself.")
            # x = lox.Lox()
            # x.error(stmt.super_class.name, "A class can't inherit from itself.")
            # raise RunTimeError(stmt.super_class.name, "A class can't inherit from itself")
        if stmt.super_class is not None:
            self.current_class = Class_type.SUBCLASS
            self.resolve(stmt.super_class) # resolve expression Variable
        if stmt.super_class is not None:
            self.begin_scope()
            self.scopes[-1]["super"] = True
        self.begin_scope()
        # self.scopes["this"] = True
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = Function_type.METHOD
            if method.name.lexeme == "init":
                declaration = Function_type.INITIALIZER
            self.resolve_function(method, declaration)
        self.end_scope()
        if stmt.super_class is not None:
            self.end_scope()
        self.current_class = enclosing_class
        # return None

    def visit_expression_stmt(self, stmt: Expression):
        self.resolve(stmt.expr)
        # return None

    def visit_function_stmt(self, stmt: Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, Function_type.FUNCTION)
        # return None

    def visit_if_stmt(self, stmt: If):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch:
            self.resolve(stmt.else_branch)
        # return None

    def visit_print_stmt(self, stmt: Print):
        self.resolve(stmt.expr)

    def visit_return_stmt(self, stmt: Return):
        if self.current_function == Function_type.NONE:
            self.error_handler.token_error(stmt.keyword, "Can't return from top-level code.")
            # lox.Lox.error(stmt.keyword, "Can't return from top-level code.")
        if stmt.value:
            if self.current_function == Function_type.INITIALIZER:
                self.error_handler.token_error(stmt.keyword, "Can't return a value from an initializer.")
                # lox.Lox.error(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve(stmt.value)
        # return None

    def visit_while_stmt(self, stmt: While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        # return None

    def visit_var_stmt(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
        # return None

    def visit_assign_expr(self, expr: Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
        # return None

    def visit_binary_expr(self, expr: Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)
        # return None

    def visit_call_expr(self, expr: Call):
        self.resolve(expr.callee)
        for arg in expr.args:
            self.resolve(arg)
        # return None

    def visit_get_expr(self, expr: Get):
        self.resolve(expr.object)
        # return None

    def visit_grouping_expr(self, expr: Grouping):
        self.resolve(expr.expression)
        # return None

    def visit_literal_expr(self, expr: Literal):
        return None

    def visit_logical_expr(self, expr: Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)
        # return None

    def visit_set_expr(self, expr: Set):
        self.resolve(expr.value)
        self.resolve(expr.object)
        # return None

    def visit_super_expr(self, expr: Super):
        if self.current_class is Class_type.NONE:
            # lox.Lox.error(expr.keyword, "Can't use 'super' outside of a class.")
            self.error_handler.token_error(expr.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class is not Class_type.SUBCLASS:
            self.error_handler.token_error(expr.keyword, "Can't use 'super' in a class with no superclass.")
            # lox.Lox.error(expr.keyword, "Can't use 'super' in a class with no superclass.")
        self.resolve_local(expr, expr.keyword)
        # return None

    def visit_this_expr(self, expr: This):
        if self.current_class == Class_type.NONE:
            self.error_handler.token_error(expr.keyword, "Can't use 'this' outside of a class.")
            # lox.Lox.error(expr.keyword, "Can't use 'this' outside of a class.")
            # return None
        self.resolve_local(expr, expr.keyword)
        # return None

    def visit_unary_expr(self, expr: Unary):
        self.resolve(expr.right)
        # return None


    def visit_variable_expr(self, expr: Variable):
        # if self.scopes and expr.name.lexeme in self.scopes[-1]:
        if len(self.scopes) != 0 and self.scopes[-1].get(expr.name.lexeme) == False:
            self.error_handler.token_error(expr.name, "Can't read local variable in its own initializer.")
            # raise lox.Lox.error(expr.name, "Can't read local variable in its own initializer.")
        self.resolve_local(expr, expr.name)
        # return None

    # def resolve(self, stmt: Stmt):
    #     stmt.accept(self)

    # def resolve(self, expr: Expr):
    #     expr.accept(self)

    def resolve(self, obj: 'Expr or Stmt'):
        obj.accept(self)

    def resolve_function(self,stmt:Function, type: Function_type):
        enclosing_function = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in stmt.params:
            self.declare(param)
            self.define(param)
        self.resolve_all(stmt.body)
        self.end_scope()
        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.error_handler.token_error(name, "Variable with this name has already been declared in this scope.")
            # raise lox.Lox.error(name, "Variable with this name has already been declared in this scope.")
        scope[name.lexeme] = False

    def define(self, name):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        scope[name.lexeme] = True

    def resolve_local(self, expr, name):
        # n = len(self.scopes)-1
        # for i in range(n, -1, -1):
        #     if name.lexeme in self.scopes[i]:
        #         self.interpreter.resolve(expr, n - i) # idk where the interpreter resolve came from
        #         return
        for idx, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, idx)
                return

