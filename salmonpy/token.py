from typing import Any, Optional
from tokentype import *

class Token:
    type: Tokentype
    lexeme: str
    literal: Any
    line: int

    def __init__(self,
                type: Tokentype,
                lexeme: str,
                literal: Optional[Any],
                line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return "{} '{}' {} {}".format(self.type,self.lexeme,self.literal,self.line)
         
    def __repr__(self) -> str:
        return "{} '{}' {}".format(self.type,self.lexeme,self.literal, self.line)

    def __eq__(self, other) -> bool:
        if not isinstance(other,Token):
            return False
        if all([self.type == other.type,self.lexeme == other.lexeme, self.literal==other.literal,self.line == other.line]):
            return True
        return False
        
