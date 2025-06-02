class SQLError(Exception):
    pass

class LexicalError(SQLError):
    def __init__(self, message, position):
        super().__init__(f"Lexical error at position {position}: {message}")

class SyntaxError(SQLError):
    def __init__(self, message, token=None):
        if token:
            super().__init__(f"Syntax error at token '{token.value}' (position {token.position}): {message}")
        else:
            super().__init__(f"Syntax error: {message}")

class SemanticError(SQLError):
    def __init__(self, message, token=None):
        if token:
            super().__init__(f"Semantic error at token '{token.value}' (position {token.position}): {message}")
        else:
            super().__init__(f"Semantic error: {message}")