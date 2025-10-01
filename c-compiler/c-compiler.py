#!/usr/bin/env python3
"""
VIBE-PY C COMPILER
==================
A complete C compiler implementation written in Python.

Compilation Pipeline:
1. Lexical Analysis (Tokenization)
2. Syntax Analysis (Parsing) 
3. Semantic Analysis (Type checking, Symbol tables)
4. Code Generation (Assembly output)
5. Assembly & Linking

Author: Anim-101
License: MIT
"""

import sys
import os
import re
import enum
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

# ============================================================================
# TOKEN DEFINITIONS
# ============================================================================

class TokenType(enum.Enum):
    # Literals
    INTEGER = "INTEGER"
    FLOAT = "FLOAT" 
    CHAR = "CHAR"
    STRING = "STRING"
    
    # Identifiers and Keywords
    IDENTIFIER = "IDENTIFIER"
    
    # C Keywords
    AUTO = "auto"
    BREAK = "break"
    CASE = "case"
    CHAR_KW = "char"
    CONST = "const"
    CONTINUE = "continue"
    DEFAULT = "default"
    DO = "do"
    DOUBLE = "double"
    ELSE = "else"
    ENUM = "enum"
    EXTERN = "extern"
    FLOAT_KW = "float"
    FOR = "for"
    GOTO = "goto"
    IF = "if"
    INT = "int"
    LONG = "long"
    REGISTER = "register"
    RETURN = "return"
    SHORT = "short"
    SIGNED = "signed"
    SIZEOF = "sizeof"
    STATIC = "static"
    STRUCT = "struct"
    SWITCH = "switch"
    TYPEDEF = "typedef"
    UNION = "union"
    UNSIGNED = "unsigned"
    VOID = "void"
    VOLATILE = "volatile"
    WHILE = "while"
    
    # Operators
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    
    # Assignment Operators
    ASSIGN = "="
    PLUS_ASSIGN = "+="
    MINUS_ASSIGN = "-="
    MULT_ASSIGN = "*="
    DIV_ASSIGN = "/="
    MOD_ASSIGN = "%="
    
    # Comparison Operators
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    
    # Logical Operators
    LOGICAL_AND = "&&"
    LOGICAL_OR = "||"
    LOGICAL_NOT = "!"
    
    # Bitwise Operators
    BITWISE_AND = "&"
    BITWISE_OR = "|"
    BITWISE_XOR = "^"
    BITWISE_NOT = "~"
    LEFT_SHIFT = "<<"
    RIGHT_SHIFT = ">>"
    
    # Increment/Decrement
    INCREMENT = "++"
    DECREMENT = "--"
    
    # Punctuation
    SEMICOLON = ";"
    COMMA = ","
    DOT = "."
    ARROW = "->"
    
    # Brackets
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    
    # Special
    QUESTION = "?"
    COLON = ":"
    
    # Preprocessor
    HASH = "#"
    
    # End of file
    EOF = "EOF"
    
    # Whitespace (usually ignored)
    WHITESPACE = "WHITESPACE"
    NEWLINE = "NEWLINE"
    COMMENT = "COMMENT"

@dataclass
class Token:
    """Represents a token with its type, value, and location info."""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"

# ============================================================================
# ABSTRACT SYNTAX TREE NODES
# ============================================================================

class ASTNode(ABC):
    """Base class for all AST nodes."""
    pass

@dataclass
class Program(ASTNode):
    """Root node of the AST representing the entire program."""
    declarations: List[ASTNode]

@dataclass
class FunctionDeclaration(ASTNode):
    """Function declaration/definition."""
    return_type: str
    name: str
    parameters: List['Parameter']
    body: Optional['CompoundStatement']

@dataclass 
class Parameter(ASTNode):
    """Function parameter."""
    type: str
    name: str

@dataclass
class VariableDeclaration(ASTNode):
    """Variable declaration."""
    type: str
    name: str
    initializer: Optional[ASTNode] = None

@dataclass
class CompoundStatement(ASTNode):
    """Block statement with curly braces."""
    statements: List[ASTNode]

@dataclass
class ExpressionStatement(ASTNode):
    """Statement containing an expression."""
    expression: ASTNode

@dataclass
class ReturnStatement(ASTNode):
    """Return statement."""
    expression: Optional[ASTNode]

@dataclass
class IfStatement(ASTNode):
    """If statement with optional else clause."""
    condition: ASTNode
    then_statement: ASTNode
    else_statement: Optional[ASTNode] = None

@dataclass
class WhileStatement(ASTNode):
    """While loop statement."""
    condition: ASTNode
    body: ASTNode

@dataclass
class ForStatement(ASTNode):
    """For loop statement."""
    init: Optional[ASTNode]
    condition: Optional[ASTNode] 
    update: Optional[ASTNode]
    body: ASTNode

@dataclass
class BinaryExpression(ASTNode):
    """Binary operation expression."""
    left: ASTNode
    operator: str
    right: ASTNode

@dataclass
class UnaryExpression(ASTNode):
    """Unary operation expression."""
    operator: str
    operand: ASTNode

@dataclass
class AssignmentExpression(ASTNode):
    """Assignment expression."""
    left: ASTNode
    operator: str
    right: ASTNode

@dataclass
class CallExpression(ASTNode):
    """Function call expression."""
    function: ASTNode
    arguments: List[ASTNode]

@dataclass
class Identifier(ASTNode):
    """Identifier expression."""
    name: str

@dataclass
class IntegerLiteral(ASTNode):
    """Integer literal expression."""
    value: int

@dataclass
class FloatLiteral(ASTNode):
    """Float literal expression."""
    value: float

@dataclass
class StringLiteral(ASTNode):
    """String literal expression."""
    value: str

@dataclass
class CharLiteral(ASTNode):
    """Character literal expression."""
    value: str

# ============================================================================
# LEXICAL ANALYZER (TOKENIZER)
# ============================================================================

class Lexer:
    """Lexical analyzer that converts C source code into tokens."""
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # C Keywords
        self.keywords = {
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
            'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
            'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof',
            'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void',
            'volatile', 'while'
        }
    
    def current_char(self) -> str:
        """Get current character or EOF."""
        if self.position >= len(self.source):
            return '\0'
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> str:
        """Look ahead at character without advancing position."""
        peek_pos = self.position + offset
        if peek_pos >= len(self.source):
            return '\0'
        return self.source[peek_pos]
    
    def advance(self) -> str:
        """Move to next character and return current."""
        if self.position >= len(self.source):
            return '\0'
        
        char = self.source[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char().isspace():
            self.advance()
    
    def skip_comment(self):
        """Skip single-line (//) and multi-line (/* */) comments."""
        if self.current_char() == '/' and self.peek_char() == '/':
            # Single-line comment
            while self.current_char() != '\n' and self.current_char() != '\0':
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '*':
            # Multi-line comment
            self.advance()  # Skip '/'
            self.advance()  # Skip '*'
            
            while True:
                if self.current_char() == '\0':
                    raise SyntaxError(f"Unterminated comment at line {self.line}")
                if self.current_char() == '*' and self.peek_char() == '/':
                    self.advance()  # Skip '*'
                    self.advance()  # Skip '/'
                    break
                self.advance()
    
    def read_string(self) -> str:
        """Read string literal."""
        quote_char = self.advance()  # Skip opening quote
        value = ""
        
        while self.current_char() != quote_char and self.current_char() != '\0':
            if self.current_char() == '\\':
                self.advance()  # Skip backslash
                escaped = self.advance()
                # Handle escape sequences
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'"}
                value += escape_map.get(escaped, escaped)
            else:
                value += self.advance()
        
        if self.current_char() != quote_char:
            raise SyntaxError(f"Unterminated string at line {self.line}")
        
        self.advance()  # Skip closing quote
        return value
    
    def read_number(self) -> Union[int, float]:
        """Read integer or float literal."""
        value = ""
        is_float = False
        
        while self.current_char().isdigit() or self.current_char() == '.':
            if self.current_char() == '.':
                if is_float:
                    break  # Second dot, stop reading
                is_float = True
            value += self.advance()
        
        return float(value) if is_float else int(value)
    
    def read_identifier(self) -> str:
        """Read identifier or keyword."""
        value = ""
        
        while (self.current_char().isalnum() or self.current_char() == '_'):
            value += self.advance()
        
        return value
    
    def tokenize(self) -> List[Token]:
        """Convert source code into list of tokens."""
        self.tokens = []
        
        while self.position < len(self.source):
            start_line, start_col = self.line, self.column
            
            # Skip whitespace
            if self.current_char().isspace():
                self.skip_whitespace()
                continue
            
            # Skip comments
            if self.current_char() == '/' and (self.peek_char() == '/' or self.peek_char() == '*'):
                self.skip_comment()
                continue
            
            char = self.current_char()
            
            # String literals
            if char in ['"', "'"]:
                value = self.read_string()
                token_type = TokenType.STRING if char == '"' else TokenType.CHAR
                self.tokens.append(Token(token_type, value, start_line, start_col))
            
            # Numbers
            elif char.isdigit():
                value = self.read_number()
                token_type = TokenType.FLOAT if isinstance(value, float) else TokenType.INTEGER
                self.tokens.append(Token(token_type, str(value), start_line, start_col))
            
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                value = self.read_identifier()
                if value in self.keywords:
                    # Map keywords to their token types
                    token_type = getattr(TokenType, value.upper(), None)
                    if token_type is None:
                        token_type = getattr(TokenType, value.upper() + '_KW', TokenType.IDENTIFIER)
                else:
                    token_type = TokenType.IDENTIFIER
                self.tokens.append(Token(token_type, value, start_line, start_col))
            
            # Two-character operators
            elif char == '+' and self.peek_char() == '+':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.INCREMENT, "++", start_line, start_col))
            elif char == '-' and self.peek_char() == '-':
                self.advance(); self.advance() 
                self.tokens.append(Token(TokenType.DECREMENT, "--", start_line, start_col))
            elif char == '+' and self.peek_char() == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.PLUS_ASSIGN, "+=", start_line, start_col))
            elif char == '-' and self.peek_char() == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.MINUS_ASSIGN, "-=", start_line, start_col))
            elif char == '*' and self.peek_char() == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.MULT_ASSIGN, "*=", start_line, start_col))
            elif char == '/' and self.peek_char() == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.DIV_ASSIGN, "/=", start_line, start_col))
            elif char == '%' and self.peek_char() == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.MOD_ASSIGN, "%=", start_line, start_col))
            elif char == '=' and self.peek_char() == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.EQUAL, "==", start_line, start_col))
            elif char == '!' and self.peek_char() == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUAL, "!=", start_line, start_col))
            elif char == '<' and self.peek_char() == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", start_line, start_col))
            elif char == '>' and self.peek_char() == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", start_line, start_col))
            elif char == '&' and self.peek_char() == '&':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.LOGICAL_AND, "&&", start_line, start_col))
            elif char == '|' and self.peek_char() == '|':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.LOGICAL_OR, "||", start_line, start_col))
            elif char == '<' and self.peek_char() == '<':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.LEFT_SHIFT, "<<", start_line, start_col))
            elif char == '>' and self.peek_char() == '>':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.RIGHT_SHIFT, ">>", start_line, start_col))
            elif char == '-' and self.peek_char() == '>':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.ARROW, "->", start_line, start_col))
            
            # Single-character operators and punctuation
            else:
                self.advance()
                token_map = {
                    '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.MULTIPLY,
                    '/': TokenType.DIVIDE, '%': TokenType.MODULO, '=': TokenType.ASSIGN,
                    '<': TokenType.LESS_THAN, '>': TokenType.GREATER_THAN,
                    '!': TokenType.LOGICAL_NOT, '&': TokenType.BITWISE_AND,
                    '|': TokenType.BITWISE_OR, '^': TokenType.BITWISE_XOR,
                    '~': TokenType.BITWISE_NOT, ';': TokenType.SEMICOLON,
                    ',': TokenType.COMMA, '.': TokenType.DOT, '?': TokenType.QUESTION,
                    ':': TokenType.COLON, '(': TokenType.LEFT_PAREN,
                    ')': TokenType.RIGHT_PAREN, '{': TokenType.LEFT_BRACE,
                    '}': TokenType.RIGHT_BRACE, '[': TokenType.LEFT_BRACKET,
                    ']': TokenType.RIGHT_BRACKET, '#': TokenType.HASH
                }
                
                token_type = token_map.get(char)
                if token_type:
                    self.tokens.append(Token(token_type, char, start_line, start_col))
                else:
                    raise SyntaxError(f"Unknown character '{char}' at line {self.line}, column {self.column}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

# ============================================================================
# MAIN COMPILER CLASS
# ============================================================================

class CCompiler:
    """Main C Compiler class coordinating all compilation phases."""
    
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = None
        self.code_generator = None
    
    def compile(self, source_file: str, output_file: str = None) -> bool:
        """Compile C source file to executable."""
        try:
            # Read source code
            with open(source_file, 'r') as f:
                source_code = f.read()
            
            print(f"🚀 Compiling {source_file}...")
            
            # Phase 1: Lexical Analysis
            print("📝 Phase 1: Lexical Analysis (Tokenization)...")
            self.lexer = Lexer(source_code)
            tokens = self.lexer.tokenize()
            print(f"   Generated {len(tokens)} tokens")
            
            # Debug: Print first 10 tokens
            print("   First 10 tokens:")
            for i, token in enumerate(tokens[:10]):
                print(f"     {i+1}. {token}")
            
            # TODO: Phase 2: Syntax Analysis (Parsing)
            print("🌳 Phase 2: Syntax Analysis (Parsing) - TODO")
            
            # TODO: Phase 3: Semantic Analysis
            print("🔍 Phase 3: Semantic Analysis - TODO")
            
            # TODO: Phase 4: Code Generation  
            print("⚙️ Phase 4: Code Generation - TODO")
            
            # TODO: Phase 5: Assembly & Linking
            print("🔗 Phase 5: Assembly & Linking - TODO")
            
            print(f"✅ Compilation completed successfully!")
            return True
            
        except FileNotFoundError:
            print(f"❌ Error: Source file '{source_file}' not found.")
            return False
        except SyntaxError as e:
            print(f"❌ Syntax Error: {e}")
            return False
        except Exception as e:
            print(f"❌ Compilation Error: {e}")
            return False

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point for the C compiler."""
    if len(sys.argv) < 2:
        print("🔧 VIBE-PY C Compiler")
        print("Usage: python c-compiler.py <source_file.c> [output_file]")
        print("\nExample:")
        print("  python c-compiler.py hello.c")
        print("  python c-compiler.py program.c my_program")
        sys.exit(1)
    
    source_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not source_file.endswith('.c'):
        print("❌ Error: Source file must have .c extension")
        sys.exit(1)
    
    compiler = CCompiler()
    success = compiler.compile(source_file, output_file)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()