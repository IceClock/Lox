import sys
from pathlib import Path
from scanner import *
from parser import *
from astPrinter import AstPrinter
from interpreter import *
from resolver import *
from error_handler import *

class Lox:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.error_handler = Error_handler()
        self.interpreter = Interpreter(self.error_handler)

    def run_file(self, path: Path):
        with open(path, "r", encoding="utf-8") as f:
            self.run(f.read())
        
        if self.error_handler.had_error:
            sys.exit(65)
        if self.error_handler.had_runtime_error:
            sys.exit(70)

    def run_prompt(self, keyboard_interrupt = False):
        while True:
            print("salmonpy> ",end="")
            try:
                if not keyboard_interrupt:
                    self.run(input())
                else:
                    raise KeyboardInterrupt()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            self.error_handler.had_error = False

    def run(self, source):
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        if self.error_handler.had_error: return
    
        # print(AstPrinter().print(expression))
        resolver = Resolver(self.interpreter)
        resolver.resolve_all(statements)

        if self.error_handler.had_error: return

        self.interpreter.interpret(statements)

    # def report(self, line, where,msg):
    #     print("[line{}] Error {}: {}".format(line,where,msg))
    #     self.had_error = True

    # def error(self, token: Token, msg:str):
    #     if (token.type == Tokentype.EOF):
    #         self.report(token.line, " at end",msg)
    #     else:
    #         self.report(token.line," at '" + token.lexeme + "'" , msg)

    # def runtime_error(self, error):
    #     # print(error.msg, "\n[line ", error.token.line,"]")
    #     print("[line ", error.token.line,"]: ", error.msg)
    #     self.had_runtime_error = True

if __name__ == "__main__":
    x = Lox()
    if len(sys.argv) > 2:
        print("Usage: salmonpy [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        x.run_file(sys.argv[1])
    else:
        x.run_prompt()
