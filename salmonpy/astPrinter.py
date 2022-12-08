
from token import Token
from tokentype import Tokentype
import parser
import scanner
from expr import *

class AstPrinter:
    # def __init__(self):
    #     pass

    def print(self, expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme ,expr.left, expr.right)
    
    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)
    
    def parenthesize(self, name: str, *exprs) -> str:
        builder = f"({name}"
        for expr in exprs:
            builder += f" {expr.accept(self)}"
        builder += ")"
        return builder

# if __name__ == "__main__":

#     expression = Binary(
#         Unary(
#             Token(Tokentype.MINUS,"-",None,1),
#             Literal(123)),
#             Token(Tokentype.STAR,"*",None,1),
#             Grouping(Literal(45.67))
#         )

#     print(AstPrinter().print(expression))