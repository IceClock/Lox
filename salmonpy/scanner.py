from token import Token
from tokentype import Tokentype
from typing import Dict,List

class Scanner:
    source: str
    tokens: List[Token]
    start: int
    current: int
    line: int

    keywords: Dict[str, Tokentype] = \
        {"and":    Tokentype.AND,
         "class":  Tokentype.CLASS,
         "else":   Tokentype.ELSE,
         "false":  Tokentype.FALSE,
         "for":    Tokentype.FOR,
         "fun":    Tokentype.FUN,
         "if":     Tokentype.IF,
         "nil":    Tokentype.NIL,
         "or":     Tokentype.OR,
         "print":  Tokentype.PRINT,
         "return": Tokentype.RETURN,
         "super":  Tokentype.SUPER,
         "this":   Tokentype.THIS,
         "true":   Tokentype.TRUE,
         "var":    Tokentype.VAR,
         "while":  Tokentype.WHILE}

    def __init__(self, source, error_handler):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.error_handler = error_handler

    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(Tokentype.EOF,"",None,self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        if c == "(":
            self.add_token(Tokentype.LEFT_PAREN)
        elif c == ")":
            self.add_token(Tokentype.RIGHT_PAREN)
        elif c == "{":
            self.add_token(Tokentype.LEFT_BRACE)
        elif c == "}":
            self.add_token(Tokentype.RIGHT_BRACE)
        elif c == ",":
            self.add_token(Tokentype.COMMA)
        elif c == ".":
            self.add_token(Tokentype.DOT)
        elif c == "-":
            self.add_token(Tokentype.MINUS)
        elif c == "+":
            self.add_token(Tokentype.PLUS)
        elif c == ";":
            self.add_token(Tokentype.SEMICOLON)
        elif c == "*":
            self.add_token(Tokentype.STAR)
        elif c == "!":
            if self.match("="):
                self.add_token(Tokentype.BANG_EQUAL)
            else:
                self.add_token(Tokentype.BANG)
        elif c == "=":
            if self.match("="):
                self.add_token(Tokentype.EQUAL_EQUAL)
            else:
                self.add_token(Tokentype.EQUAL)
        elif c == "<":
            if self.match("="):
                self.add_token(Tokentype.LESS_EQUAL)
            else:
                self.add_token(Tokentype.LESS)
        elif c == ">":
            if self.match("="):
                self.add_token(Tokentype.GREATER_EQUAL)
            else:
                self.add_token(Tokentype.GREATER)
        elif c == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            elif self.match("*"):
                block_comment_end_found = False
                while not block_comment_end_found:
                    if self.match("\n"):
                        self.line += 1
                    elif self.match("*"):
                        if self.match("/"):
                            block_comment_end_found = True
                    elif self.is_at_end():
                        break
                    else:
                        self.advance()
                if not block_comment_end_found:
                    # lox.Lox.error(self.line,"Unterminated comment block")
                    self.error_handler.scanner_error(self.line,"Unterminated comment block" )
                if self.is_at_end(): return
                found_new_line = False
                while not found_new_line:
                    if self.match("\n"):
                        found_new_line = True
                        self.line += 1
                    elif self.match(" ") or self.match("\t"):
                        continue
                    elif self.is_at_end():
                        break
                    else:
                        # lox.Lox.error(self.line, "Unterminated comment block")
                        self.error_handler.scanner_error(self.line, "Unterminated comment block")
                        self.advance()
            else:
                self.add_token(Tokentype.SLASH)
        elif c == " ":
            pass
        elif c == "\r":
            pass
        elif c == "\n":
            self.line += 1
        elif c == "\"":
            self.string()
        else:
            if self.is_digit(c):
                self.number()
            elif self.is_alpha(c):
                self.identifier()
            else:
                # l = lox.Lox()
                # l.report(self.line, c, "unexpected character")
                self.error(self.line, f"Unexpected character: {c}")

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        # fractional 
        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
        self.add_token_with_literal(Tokentype.NUMBER, float(self.source[self.start:self.current]))

    def identifier(self):
        # while self.is_alpha(self.peek()): self.advance()
        while self.is_alphanumeric(self.peek()):
            self.advance()
        txt = self.source[self.start:self.current]

        type = self.keywords.get(txt)
        if type is None:
            type = Tokentype.IDENTIFIER
        self.add_token(type)

    def string(self) :
        while self.peek() != "\"" and not self.is_at_end():
            if self.peek() == "\n": 
                # self.line_number += 1
                self.line += 1
            self.advance()

        # Unterminated string.
        if self.is_at_end():
            self.error(self.line, "Unterminated string.")
            # lox.Lox.error(self.line_number, "Unterminated string.")
            return
        # The closing "."
        self.advance()
        # Trim the surrounding quotes.
        value = self.source[self.start + 1:self.current - 1]
        self.add_token_with_literal(Tokentype.STRING, value)

    def match(self, expected) -> bool:
        if self.is_at_end(): return False
        if self.source[self.current] != expected: return False
        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end(): return "\0"
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source): return "\0"
        return self.source[self.current + 1]

    def is_alpha(self, c):
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or c == "_"

    def is_alphanumeric(self, c):
        return self.is_digit(c) or self.is_alpha(c)
    
    def is_digit(self, c):
        return c >= "0" and c <= "9"

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self):
        self.current += 1
        return self.source[self.current-1]

    def add_token(self, type):
        self.add_token_with_literal(type,None)

    def add_token_with_literal(self, type, literal):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal,self.line))

    def error(self, line, msg):
        self.error_handler.scanner_error(line, msg)
