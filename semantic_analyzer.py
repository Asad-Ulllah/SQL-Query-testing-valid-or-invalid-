import json
from errors import SemanticError

class SemanticAnalyzer:
    def __init__(self, schema_file):
        with open(schema_file) as f:
            self.schema = json.load(f)
    
    def analyze(self, ast):
        self._check_tables_exist(ast)
        self._check_columns_exist(ast)
        self._check_aggregate_functions(ast)
    
    def _check_tables_exist(self, ast):
        for table in ast.tables:
            if table.name not in self.schema['tables']:
                raise SemanticError(f"Table '{table.name}' does not exist")
    
    def _check_columns_exist(self, ast):
        # Check columns in SELECT clause
        for column in ast.columns:
            if column.name == '*':
                continue
            self._resolve_column(column.name, ast.tables)
        
        # Check columns in WHERE clause
        if ast.where_conditions:
            self._check_condition_columns(ast.where_conditions, ast.tables)
        
        # Check columns in GROUP BY
        if ast.group_by:
            for column in ast.group_by:
                self._resolve_column(column.name, ast.tables)
        
        # Check columns in ORDER BY
        if ast.order_by:
            for column, _ in ast.order_by:
                self._resolve_column(column.name, ast.tables)
    
    def _check_condition_columns(self, condition, tables):
        if isinstance(condition.left, Column):
            self._resolve_column(condition.left.name, tables)
        elif isinstance(condition.left, Condition):
            self._check_condition_columns(condition.left, tables)
        
        if isinstance(condition.right, Column):
            self._resolve_column(condition.right.name, tables)
        elif isinstance(condition.right, Condition):
            self._check_condition_columns(condition.right, tables)
    
    def _resolve_column(self, column_name, tables):
        # Handle table.column notation
        if '.' in column_name:
            table_part, column_part = column_name.split('.')
            if table_part not in [t.name for t in tables] and table_part not in [t.alias for t in tables if t.alias]:
                raise SemanticError(f"Table '{table_part}' not in FROM clause")
            
            table_name = next((t.name for t in tables if t.name == table_part or t.alias == table_part), None)
            if column_part not in self.schema['tables'][table_name]['columns']:
                raise SemanticError(f"Column '{column_part}' does not exist in table '{table_name}'")
        else:
            # Column without table prefix - must be unambiguous
            found_tables = []
            
            for table in tables:
                table_name = table.name
                if column_name in self.schema['tables'][table_name]['columns']:
                    found_tables.append(table_name)
            
            if len(found_tables) == 0:
                raise SemanticError(f"Column '{column_name}' does not exist in any table")
            if len(found_tables) > 1:
                raise SemanticError(f"Column '{column_name}' is ambiguous (exists in {', '.join(found_tables)})")
    
    def _check_aggregate_functions(self, ast):
        if ast.group_by:
            # In GROUP BY queries, non-aggregated columns in SELECT must appear in GROUP BY
            pass  # Implementation left as exercise