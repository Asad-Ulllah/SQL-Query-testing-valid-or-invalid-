from errors import SyntaxError

class ASTNode:
    pass

class SelectStatement(ASTNode):
    def __init__(self):
        self.columns = []
        self.tables = []
        self.where_conditions = None
        self.group_by = None
        self.order_by = None
    
    def __repr__(self):
        return f"Select(columns={self.columns}, tables={self.tables}, where={self.where_conditions}, group_by={self.group_by}, order_by={self.order_by})"

class Column(ASTNode):
    def __init__(self, name, alias=None):
        self.name = name
        self.alias = alias
    
    def __repr__(self):
        if self.alias:
            return f"Column({self.name} AS {self.alias})"
        return f"Column({self.name})"

class Table(ASTNode):
    def __init__(self, name, alias=None):
        self.name = name
        self.alias = alias
    
    def __repr__(self):
        if self.alias:
            return f"Table({self.name} AS {self.alias})"
        return f"Table({self.name})"

class Condition(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    
    def __repr__(self):
        return f"Condition({self.left} {self.op} {self.right})"

class SQLParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
    
    def error(self, message):
        raise SyntaxError(message, self.current_token)
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def expect(self, token_type, error_message=None):
        if not self.current_token:
            raise SyntaxError("Unexpected end of input", None)
        if self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            error_msg = error_message or f"Expected {token_type}, got {self.current_token.type if self.current_token else 'EOF'}"
            raise SyntaxError(error_msg, self.current_token)
    
    def parse(self):
        if not self.tokens:
            raise SyntaxError("No tokens to parse", None)
        
        stmt = self.select_statement()
        if self.current_token and self.current_token.type != 'EOF':
            raise SyntaxError(f"Unexpected token {self.current_token.type} at end of query", self.current_token)
        return stmt
    
    def select_statement(self):
        self.expect('SELECT', "SELECT query must begin with SELECT keyword")
        
        stmt = SelectStatement()
        stmt.columns = self.column_list()
        
        self.expect('FROM', "SELECT query must contain FROM clause")
        stmt.tables = self.table_list()
        
        if self.current_token and self.current_token.type == 'WHERE':
            self.advance()  # Skip WHERE
            stmt.where_conditions = self.condition()
        
        if self.current_token and self.current_token.type == 'GROUP':
            self.advance()  # Skip GROUP
            self.expect('BY', "GROUP must be followed by BY")
            stmt.group_by = self.column_reference_list()
        
        if self.current_token and self.current_token.type == 'ORDER':
            self.advance()  # Skip ORDER
            self.expect('BY', "ORDER must be followed by BY")
            stmt.order_by = self.order_list()
        
        return stmt
    
    def column_list(self):
        columns = []
        
        # Handle SELECT *
        if self.current_token and self.current_token.type == '*':
            columns.append(Column('*'))
            self.advance()
            # After *, there should be no more columns
            if self.current_token and self.current_token.type == ',':
                raise SyntaxError("Cannot have additional columns after *", self.current_token)
            return columns
        
        # First column is required
        if not self.current_token or self.current_token.type not in ('IDENTIFIER', '*'):
            raise SyntaxError("Expected column name or *", self.current_token)
        
        columns.append(self.column_reference())
        
        # Additional columns (comma-separated)
        while self.current_token and self.current_token.type == ',':
            self.advance()  # Skip comma
            columns.append(self.column_reference())
        
        return columns
    
    def column_reference(self):
        if not self.current_token or self.current_token.type not in ('IDENTIFIER', '*'):
            raise SyntaxError("Expected column name or *", self.current_token)
        
        column_name = self.current_token.value
        self.advance()  # Skip column name
        
        alias = None
        if self.current_token and self.current_token.type == 'AS':
            self.advance()  # Skip AS
            if not self.current_token or self.current_token.type != 'IDENTIFIER':
                raise SyntaxError("Expected alias name after AS", self.current_token)
            alias = self.current_token.value
            self.advance()  # Skip alias
        elif self.current_token and self.current_token.type == 'IDENTIFIER':
            # Implicit alias
            alias = self.current_token.value
            self.advance()  # Skip alias
        
        return Column(column_name, alias)
    
    def column_reference_list(self):
        columns = [self.column_reference()]
        
        while self.current_token and self.current_token.type == ',':
            self.advance()  # Skip comma
            columns.append(self.column_reference())
        
        return columns
    
    def table_list(self):
        tables = [self.table_reference()]
        
        while self.current_token and self.current_token.type == ',':
            self.advance()  # Skip comma
            tables.append(self.table_reference())
        
        return tables
    
    def table_reference(self):
        if not self.current_token or self.current_token.type != 'IDENTIFIER':
            raise SyntaxError("Expected table name", self.current_token)
        
        table_name = self.current_token.value
        self.advance()  # Skip table name
        
        alias = None
        if self.current_token and self.current_token.type == 'AS':
            self.advance()  # Skip AS
            if not self.current_token or self.current_token.type != 'IDENTIFIER':
                raise SyntaxError("Expected table alias after AS", self.current_token)
            alias = self.current_token.value
            self.advance()  # Skip alias
        elif self.current_token and self.current_token.type == 'IDENTIFIER':
            # Implicit alias
            alias = self.current_token.value
            self.advance()  # Skip alias
        
        return Table(table_name, alias)
    
    def condition(self):
        left = self.expression()
        
        if not self.current_token or self.current_token.type != 'OPERATOR':
            raise SyntaxError("Expected comparison operator", self.current_token)
        
        op = self.current_token.value
        self.advance()  # Skip operator
        right = self.expression()
        
        return Condition(left, op, right)
    
    def expression(self):
        if not self.current_token:
            raise SyntaxError("Unexpected end of input in expression", None)
        
        if self.current_token.type in ('INTEGER', 'FLOAT', 'STRING'):
            value = self.current_token.value
            self.advance()
            return value
        elif self.current_token.type == 'IDENTIFIER':
            return self.column_reference()
        else:
            raise SyntaxError(f"Unexpected token {self.current_token.type} in expression", self.current_token)
    
    def order_list(self):
        orders = [self.order_item()]
        
        while self.current_token and self.current_token.type == ',':
            self.advance()  # Skip comma
            orders.append(self.order_item())
        
        return orders
    
    def order_item(self):
        column = self.column_reference()
        direction = 'ASC'  # Default
        
        if self.current_token and self.current_token.type in ('ASC', 'DESC'):
            direction = self.current_token.type
            self.advance()  # Skip direction
        
        return (column, direction)