import re
from errors import LexicalError

class Token:
    def __init__(self, type, value, position):
        self.type = type
        self.value = value
        self.position = position
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', pos={self.position})"

class SQLLexer:
    KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'ORDER', 'HAVING',
        'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'ON',
        'AND', 'OR', 'NOT', 'AS', 'DISTINCT', 'ASC', 'DESC',
        'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'
    }
    
    OPERATORS = {
        '=', '<', '>', '<=', '>=', '<>', '!=', '+', '-', '*', '/', '(', ')', ',', ';'
    }
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return Token('FLOAT', float(result), self.pos)
        
        return Token('INTEGER', int(result), self.pos)
    
    def string(self):
        result = ''
        quote = self.current_char
        self.advance()  # skip opening quote
        
        while self.current_char is not None and self.current_char != quote:
            result += self.current_char
            self.advance()
        
        if self.current_char != quote:
            raise LexicalError("Unterminated string", self.pos)
        
        self.advance()  # skip closing quote
        return Token('STRING', result, self.pos)
    
    def identifier(self):
        result = ''
        while (self.current_char is not None and 
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        
        upper_result = result.upper()
        if upper_result in self.KEYWORDS:
            return Token(upper_result, upper_result, self.pos)
        else:
            return Token('IDENTIFIER', result, self.pos)
    
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isdigit():
                return self.number()
            
            if self.current_char in ('"', "'"):
                return self.string()
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            
            # Check for multi-character operators
            if self.current_char + (self.text[self.pos+1] if self.pos+1 < len(self.text) else '') in ('<=', '>=', '<>', '!='):
                op = self.current_char + self.text[self.pos+1]
                self.advance()
                self.advance()
                return Token('OPERATOR', op, self.pos)
            
            if self.current_char in self.OPERATORS:
                op = self.current_char
                self.advance()
                return Token('OPERATOR', op, self.pos)
            
            raise LexicalError(f"Unexpected character: '{self.current_char}'", self.pos)
        
        return Token('EOF', None, self.pos)
    
    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == 'EOF':
                break
        return tokens