from expr import *
from token import *
from tokentype import *
from runTimeError import *
from stmt import *
from lox_function import *
from lox_class import *
from clock import *
from environment import *
from callable import *

class Interpreter(Expr_visitor,Stmt_visitor):
    def __init__(self, error_handler):
        self.globals = Environment()
        self.globals.define("clock", Clock())
        self.environment = self.globals
        self.locals = {}
        self.error_handler = error_handler
        
    # environment = Environment()

    # def interpret(self, expr: Expr):
    #     try:
    #         value = self.evaluate(expr)
    #         print(self.stringify(value))
    #     except RunTimeError as error:
    #         Lox.runtime_error(error)

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RunTimeError as error:
            self.error_handler.runtime_error(error)

    def visit_literal_expr(self, expr: Literal) -> str:
        return expr.value

    def visit_logical_expr(self, expr: Logical):
        left = self.evaluate(expr.left)
        if expr.operator.type == Tokentype.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)

    def visit_set_expr(self, expr: Set):
        object  = self.evaluate(expr.object)
        if not isinstance(object, Lox_instance):
            raise RunTimeError(expr.name, "Only instances have fields.")
        value = self.evaluate(expr.value)
        object.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: Super):
        distance = self.locals[expr]
        super_class = self.environment.get_at(distance, "super")
        object = self.environment.get_at(distance - 1, "this")
        method = super_class.find_method(expr.method.lexeme)
        if method is None:
            raise RunTimeError(expr.method, "Undefined property '" + expr.method.lexeme + "'.")
        return method.bind(object)

    def visit_this_expr(self, expr:This):
        return self.lookup_variable(expr.keyword, expr)

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def execute(self, statement: Stmt):
        statement.accept(self)

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth

    def execute_block(self, statements, environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_block_stmt(self, stmt: Block):
        # self.execute_block(stmt.statements, self.environment)
        self.execute_block(stmt.statements, Environment(enclosing=self.environment))
        # return None

    def visit_class_stmt(self, stmt: Class):
        super_class = None
        if stmt.super_class is not None:
            super_class = self.evaluate(stmt.super_class)
            if not isinstance(super_class, Lox_class):
                raise RunTimeError(stmt.super_class.name, "Superclass must be a class.")
        self.environment.define(stmt.name.lexeme, None) # do i need this?
        if stmt.super_class is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", super_class)
        methods = {}
        for method in stmt.methods:
            # function = Lox_function(method, self.environment)
            function = Lox_function(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function
        # klass = Lox_class(stmt.name.lexeme, methods)
        klass = Lox_class(stmt.name.lexeme, super_class, methods)
        if super_class is not None:
            self.environment = self.environment.enclosing
        self.environment.assign(stmt.name, klass)
        # return None

    def visit_expression_stmt(self, stmt: Expression):
        self.evaluate(stmt.expr)
        # return None

    def visit_function_stmt(self, stmt: Function):
        # function = Lox_function(stmt, self.environment) ## if it doesnt work check the self.environment
        function = Lox_function(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)
        # return None

    def visit_if_stmt(self, stmt: If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        # return None

    def visit_print_stmt(self, stmt: Print) -> str:
        value = self.evaluate(stmt.expr)
        print(self.stringify(value))
        # return None
        # return super().visit_print_stmt(stmt)

    def visit_return_stmt(self, stmt: Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise Return_exception(value)

    def visit_var_stmt(self, stmt: Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        # return None

    def visit_while_stmt(self, stmt: While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        # return None

    def visit_assign_expr(self, expr: Assign):
        value = self.evaluate(expr.value)
        # self.environment.assign(expr.name, value)
        distance = self.locals.get(expr)
        if distance is not None:
        # if expr in self.locals:
            self.environment.assign_at(self.locals[expr], expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_unary_expr(self, expr: Unary):
        right: Expr = self.evaluate(expr.right)
        if expr.operator.type == Tokentype.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        if expr.operator.type == Tokentype.BANG:
            return not self.is_truthy(right)

    def visit_variable_expr(self, expr: Variable):
        # return self.environment.get(expr.name)
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name, expr):
        # distance = self.locals.get(expr)
        # if distance is not None:
        #     return self.environment.get_at(distance, name.lexeme)
        if expr in self.locals:
            distance = self.locals[expr] ## if you have a problem with this change it to .get(expr)
            if distance is not None:
                return self.environment.get_at(distance, name.lexeme)
        return self.globals.get(name)
    
    def check_number_operand(self, operator: Token, operand: Expr):
        if type(operand) is float: return
        raise RunTimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: Expr, right: Expr):
        if (type(left) is float and type(right) is float): return
        raise RunTimeError(operator, "Operands must be numbers.")

    def is_truthy(self, expr: Expr):
        if expr is None: return False
        if type(expr) is bool:
            return expr
        return True

    def visit_binary_expr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right= self.evaluate(expr.right)

        if expr.operator.type is Tokentype.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.type is Tokentype.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type is Tokentype.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type is Tokentype.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        elif expr.operator.type is Tokentype.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.type is Tokentype.SLASH:
            self.check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        elif expr.operator.type is Tokentype.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        elif expr.operator.type is Tokentype.PLUS: # this is used for numbers and strings
            if (type(left) is float and type(right) is float):
                return float(left) + float(right)
            elif (type(left) is str and type(right) is str):
                return str(left) + str(right)
            raise RunTimeError(expr.operator, "Operands must be two numbers or two strings.")
        elif expr.operator.type is Tokentype.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif expr.operator.type is Tokentype.EQUAL_EQUAL:
            return self.is_equal(left, right)
        # unreachable
        return None

    def visit_call_expr(self, expr: Call):
        calle = self.evaluate(expr.callee)
        # arguments = [self.evaluate(arg) for arg in expr.args]
        if not isinstance(calle, Callable):
            raise RunTimeError(expr.paren,"Can only call functions and classes.")
        arguments = [self.evaluate(arg) for arg in expr.args]
        if len(arguments) != calle.arity():
            raise RunTimeError(expr.paren, f"Expected {calle.arity()} arguments but got {len(arguments)}.")
            # raise RunTimeError(expr.paren, "Expected "+ calle.arity() + " arguments but got " + len(arguments)+".")
        return calle.call(self,arguments)

    def visit_get_expr(self, expr: Get):
        object = self.evaluate(expr.object)
        if isinstance(object, Lox_instance):
            return object.get(expr.name)
        self.error_handler.token_error(expr.name,"Only instances have properties.")

    def is_equal(self, left, right):
        if left is None and right is None: 
            return True
        if isinstance(left, bool) or isinstance(right, bool):
            return left is right
        return left == right

    def stringify(self, obj):
        if obj is None: return "nil"
        elif type(obj) is float:
            txt = str(obj)
            if txt.endswith(".0"):
                txt = txt[0:len(txt)-2]
            return txt
        return str(obj)
    