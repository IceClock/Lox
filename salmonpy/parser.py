from token import Token
from tokentype import Tokentype
from typing import List, Optional
from expr import *
from stmt import *
"""
expression     → equality ;
equality       → comparison ( ( "!=" | "==" ) comparison )* ;
comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term           → factor ( ( "-" | "+" ) factor )* ;
factor         → unary ( ( "/" | "*" ) unary )* ;
unary          → ( "!" | "-" ) unary
               | primary ;
primary        → NUMBER | STRING | "true" | "false" | "nil"
               | "(" expression ")" ;
"""
class ParseError(Exception):
    pass
    # def __init__(self, token, msg):
    #     self.token = token
    #     self.msg = msg
    #     super().__init__(self.msg)

class Parser:

    tokens: List[Token]
    current: int

    def __init__(self,tokens_list, error_handler):
        self.tokens = tokens_list
        self.current = 0
        self.error_handler = error_handler
        # self.interpreter = interpreter

    # def parse(self):
    #     # return self.expression()
    #     try:
    #         return self.expression()
    #     except ParseError as error:
    #         return None

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while (not self.is_at_end()):
            # statements.append(self.statement())
            statements.append(self.declaration())
        return statements

    def expression(self):
        return self.assignment()
        # return self.equality()

    def declaration(self):
        try:
            if self.match(Tokentype.CLASS):
                return self.class_declaration()
            if self.match(Tokentype.FUN):
                return self.function("function")
            if self.match(Tokentype.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError as error:
            self.synchronize()
            return None

    def class_declaration(self):
        name = self.consume(Tokentype.IDENTIFIER, "Expect class name.")
        super_class = None
        if self.match(Tokentype.LESS):
            self.consume(Tokentype.IDENTIFIER,"Expect superclass name.")
            super_class = Variable(self.previous())
        self.consume(Tokentype.LEFT_BRACE, "Expect '{' before class body.")
        methods = []
        while ((not self.check(Tokentype.RIGHT_BRACE)) and (not self.is_at_end())):
            methods.append(self.function("method"))
        self.consume(Tokentype.RIGHT_BRACE, "Expect '}' after class body.")
        # return Class(name, methods)
        return Class(name, super_class, methods)

    def statement(self):
        if self.match(Tokentype.FOR):
            return self.for_statement()
        if self.match(Tokentype.IF):
            return self.if_statement()
        if self.match(Tokentype.PRINT):
            return self.print_statement()
        if self.match(Tokentype.RETURN):
            return self.return_statement()
        if self.match(Tokentype.WHILE):
            return self.while_statement()
        if self.match(Tokentype.LEFT_BRACE):
            return Block(self.block())
        return self.expression_statement()

    def for_statement(self):
        self.consume(Tokentype.LEFT_PAREN,"Expect '(' after 'for'.")
        # inititializer = None # statement type
        # initializer
        if self.match(Tokentype.SEMICOLON):
            inititializer = None
        elif self.match(Tokentype.VAR):
            inititializer = self.var_declaration()
        else:
            inititializer = self.expression_statement()
        # conidition
        condition = None # expr type
        if not self.check(Tokentype.SEMICOLON):
            condition = self.expression()
        self.consume(Tokentype.SEMICOLON,"Expect ';' after loop condition.")

        #increment
        increment = None # expr type
        if not self.check(Tokentype.RIGHT_PAREN):
            increment = self.expression()
        self.consume(Tokentype.RIGHT_PAREN,"Expect ')' after for clauses.")

        body = self.statement()
        if increment is not None:
            # body = Block([body, Expression(increment)])
            body = Block([body, increment])
        if condition is None:
            condition = Literal(True)
        body = While(condition,body)
        if inititializer is not None:
            body = Block([inititializer,body])
        return body

    def if_statement(self):
        self.consume(Tokentype.LEFT_PAREN,"Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(Tokentype.RIGHT_PAREN,"Expect ')' after if condition.")

        then_branch = self.statement()
        else_branch = None
        if self.match(Tokentype.ELSE):
            else_branch = self.statement()
        return If(condition,then_branch,else_branch)

    def print_statement(self)-> Stmt:
        value = self.expression()
        self.consume(Tokentype.SEMICOLON,"Expect ';' after value.")
        return Print(value)

    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check(Tokentype.SEMICOLON):
            value = self.expression()
        self.consume(Tokentype.SEMICOLON,"Expect ';' after return value.")
        return Return(keyword, value)

    def var_declaration(self):
        name = self.consume(Tokentype.IDENTIFIER, "Expect variable name.")
        initializer = None
        if (self.match(Tokentype.EQUAL)):
            initializer = self.expression()
        self.consume(Tokentype.SEMICOLON,"Expect ';' after variable declaration.")
        return Var(name, initializer)

    def while_statement(self):
        self.consume(Tokentype.LEFT_PAREN,"Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(Tokentype.RIGHT_PAREN,"Expect ')' after condition.")
        body = self.statement()
        return While(condition, body)

    def expression_statement(self):
        expr = self.expression()
        self.consume(Tokentype.SEMICOLON,"Expect ';' after expression.")
        return Expression(expr)

    def function(self, kind) -> Function:
        name: Token = self.consume(Tokentype.IDENTIFIER, "Excpect "+ kind + " name.")
        self.consume(Tokentype.LEFT_PAREN,"Expect '(' after " + kind + " name.")
        parameters = []
        if not self.check(Tokentype.RIGHT_PAREN):
            while True:#self.match(Tokentype.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(),"Can't have more than 255 parameters.")
                parameters.append(self.consume(Tokentype.IDENTIFIER,"Expect parameter name."))
                if not self.match(Tokentype.COMMA): break
        self.consume(Tokentype.RIGHT_PAREN,"Expect ')' after parameters.")
        self.consume(Tokentype.LEFT_BRACE, "Expect '{' before " + kind + " body.")
        body = self.block()
        return Function(name,parameters,body)

    def block(self):
        statements = []
        while ((not self.check(Tokentype.RIGHT_BRACE)) and (not self.is_at_end())):
            statements.append(self.declaration())
        self.consume(Tokentype.RIGHT_BRACE,"Expect '}' after block.")
        return statements

    def assignment(self):
        # expr = self.equality()
        expr = self.Or()
        if self.match(Tokentype.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
            # if type(expr) is Variable:
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
            # elif type(expr) is Get:
                # get = expr
                return Set(expr.object, expr.name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def Or(self):
        expr = self.And()
        while self.match(Tokentype.OR):
            operator = self.previous()
            right = self.And()
            expr = Logical(expr, operator, right)
        return expr

    def And(self):
        expr = self.equality()
        while self.match(Tokentype.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr


    def equality(self):
        expr: Expr = self.comparison()
        while (self.match(Tokentype.BANG_EQUAL, 
                          Tokentype.EQUAL_EQUAL)):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr: Expr = self.term()

        while (self.match(Tokentype.GREATER, 
                          Tokentype.GREATER_EQUAL,
                          Tokentype.LESS,
                          Tokentype.LESS_EQUAL)):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self):
        expr: Expr = self.factor()
        while (self.match(Tokentype.MINUS,
                          Tokentype.PLUS)):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr: Expr = self.unary()
        while (self.match(Tokentype.SLASH,
                          Tokentype.STAR)):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if (self.match(Tokentype.BANG,
                       Tokentype.MINUS)):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return Unary(operator, right)
            # return self.unary(operator, right)
        # return self.primary()
        return self.call()

    def finish_call(self, calle: Expr):
        arguments = []
        if not self.check(Tokentype.RIGHT_PAREN):
            # while self.match(Tokentype.COMMA):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(Tokentype.COMMA): break
        paren = self.consume(Tokentype.RIGHT_PAREN,"Expect ')' after arguments.")
        return Call(calle, paren, arguments)

    def call(self):
        expr = self.primary()
        while (True):
            if self.match(Tokentype.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(Tokentype.DOT):
                name = self.consume(Tokentype.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        return expr

    def primary(self):
        if self.match(Tokentype.FALSE):
            return Literal(False)
        elif self.match(Tokentype.TRUE):
            return Literal(True)
        elif self.match(Tokentype.NIL):
            return Literal(None)
        elif self.match(Tokentype.NUMBER, Tokentype.STRING):
            return Literal(self.previous().literal)
        elif self.match(Tokentype.SUPER):
            keyword = self.previous()
            self.consume(Tokentype.DOT, "Expect '.' after 'super'.")
            method = self.consume(Tokentype.IDENTIFIER, "Expect superclass method name.")
            return Super(keyword, method)
        elif self.match(Tokentype.THIS):
            return This(self.previous())
        elif self.match(Tokentype.IDENTIFIER):
            return Variable(self.previous())
        elif (self.match(Tokentype.LEFT_PAREN)):
            expr: Expr = self.expression()
            self.consume(Tokentype.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression.")

    def match(self, *token_types: Tokentype) -> bool:
        for token_type in token_types:
            if (self.check(token_type)):
                self.advance()
                return True
        return False

    def consume(self, type:Tokentype, msg: str):
        if (self.check(type)): return self.advance()
        raise self.error(self.peek(), msg)
    
    def check(self,token_type: Tokentype):
        if self.is_at_end(): return False
        return self.peek().type == token_type

    def advance(self) -> Token:
        if (not (self.is_at_end())): self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == Tokentype.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def error(self, token: Token, msg: str):
        # self.interpreter.error(token,msg)
        self.error_handler.token_error(token, msg)
        # self.error(token,msg)
        raise ParseError()

    def synchronize(self):
        self.advance()
        while (not self.is_at_end()):
            if (self.previous().type == Tokentype.SEMICOLON): return
            keywords = {Tokentype.CLASS, 
                        Tokentype.FUN, 
                        Tokentype.VAR, 
                        Tokentype.FOR, 
                        Tokentype.IF, 
                        Tokentype.WHILE,  
                        Tokentype.PRINT, 
                        Tokentype.RETURN}
            if self.peek().type in keywords: return
            self.advance()