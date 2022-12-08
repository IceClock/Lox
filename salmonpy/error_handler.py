from tokentype import *

class Error_handler:
    def __init__(self) -> None:
        self.had_error = False
        self.had_runtime_error = False

    def scanner_error(self, line, msg):
        self.report(line, f"Error: {msg}")

    def token_error(self, token, msg):
        if token.type == Tokentype.EOF:
            self.report(token.line, f"Error at end: {msg}")
        else:
            self.report(token.line, f"Error at '{token.lexeme}': {msg}")

    def report(self,line, msg):
        print(f"[line {line}] {msg}")
        self.had_error = True

    def runtime_error(self, error):
        # print(error.message, f"[line {error.token.line}]")
        print(f"[line {error.token.line}]:", error.message)
        self.had_runtime_error = True