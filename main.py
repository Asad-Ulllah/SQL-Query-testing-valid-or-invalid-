import utils.transport
import utils.session
import json
from lexer import SQLLexer, Token
from parser import SQLParser
from semantic_analyzer import SemanticAnalyzer
from errors import LexicalError, SyntaxError, SemanticError

def load_schema(schema_file):
    try:
        with open(schema_file) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file '{schema_file}' not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in schema file '{schema_file}'")
        return None

def validate_query(query, schema_file):
    try:
        # Lexical analysis
        lexer = SQLLexer(query)
        tokens = lexer.tokenize()
        
        print("\nTokens:")
        for token in tokens:
            print(token)
        
        # Syntactic analysis
        parser = SQLParser(tokens)
        ast = parser.parse()
        
        print("\nAST:")
        print(ast)
        
        # Semantic analysis
        analyzer = SemanticAnalyzer(schema_file)
        analyzer.analyze(ast)
        
        print("\nValidation successful! The SQL query is valid.")
        return True
    
    except LexicalError as e:
        print(f"\nLexical Error: {e}")
    except SyntaxError as e:
        print(f"\nSyntax Error: {e}")
    except SemanticError as e:
        print(f"\nSemantic Error: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    return False

def main():
    print("SQL Query Validator")
    print("------------------")
   
    schema_file = "database_schema.json"
    
    while True:
        print("\nEnter your SQL query (or 'exit' to quit):")
        query = input("> ")
        
        if query.lower() == 'exit':
            break
        
        if not query.strip():
            continue
        
        validate_query(query, schema_file)

if __name__ == "__main__":
    main()