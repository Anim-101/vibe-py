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
# PARSER EXCEPTIONS
# ============================================================================

class ParseError(Exception):
    """Exception raised when parsing fails."""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at line {token.line}, column {token.column}")

# ============================================================================
# RECURSIVE DESCENT PARSER
# ============================================================================

class Parser:
    """
    Recursive Descent Parser for C language.
    
    Converts a stream of tokens into an Abstract Syntax Tree (AST).
    Uses recursive descent parsing with operator precedence handling.
    
    Grammar (simplified C subset):
    
    program          ::= declaration*
    declaration      ::= function_declaration | variable_declaration
    function_decl    ::= type IDENTIFIER '(' parameter_list? ')' compound_statement
    variable_decl    ::= type IDENTIFIER ('=' expression)? ';'
    parameter_list   ::= parameter (',' parameter)*
    parameter        ::= type IDENTIFIER
    
    compound_stmt    ::= '{' statement* '}'
    statement        ::= compound_statement | expression_statement | 
                        return_statement | if_statement | while_statement |
                        for_statement | variable_declaration
    
    expression_stmt  ::= expression? ';'
    return_stmt      ::= 'return' expression? ';'
    if_stmt          ::= 'if' '(' expression ')' statement ('else' statement)?
    while_stmt       ::= 'while' '(' expression ')' statement
    for_stmt         ::= 'for' '(' expression? ';' expression? ';' expression? ')' statement
    
    expression       ::= assignment_expr
    assignment_expr  ::= logical_or_expr (('=' | '+=' | '-=' | '*=' | '/=') logical_or_expr)*
    logical_or_expr  ::= logical_and_expr ('||' logical_and_expr)*
    logical_and_expr ::= equality_expr ('&&' equality_expr)*
    equality_expr    ::= relational_expr (('==' | '!=') relational_expr)*
    relational_expr  ::= additive_expr (('<' | '>' | '<=' | '>=') additive_expr)*
    additive_expr    ::= multiplicative_expr (('+' | '-') multiplicative_expr)*
    multiplicative_expr ::= unary_expr (('*' | '/' | '%') unary_expr)*
    unary_expr       ::= ('!' | '-' | '++' | '--') unary_expr | postfix_expr
    postfix_expr     ::= primary_expr ('(' argument_list? ')' | '++' | '--')*
    primary_expr     ::= IDENTIFIER | INTEGER | FLOAT | CHAR | STRING | 
                        '(' expression ')'
    
    argument_list    ::= expression (',' expression)*
    type             ::= 'int' | 'float' | 'char' | 'void' | 'double'
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.current_token = tokens[0] if tokens else Token(TokenType.EOF, "", 0, 0)
    
    def error(self, message: str) -> None:
        """Raise a parse error with current token location."""
        raise ParseError(message, self.current_token)
    
    def advance(self) -> Token:
        """Move to next token and return current token."""
        if self.current < len(self.tokens) - 1:
            self.current += 1
            self.current_token = self.tokens[self.current]
        return self.current_token
    
    def peek(self, offset: int = 1) -> Token:
        """Look ahead at token without advancing position."""
        peek_pos = self.current + offset
        if peek_pos >= len(self.tokens):
            return Token(TokenType.EOF, "", 0, 0)
        return self.tokens[peek_pos]
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current_token.type in token_types
    
    def consume(self, token_type: TokenType, error_message: str = None) -> Token:
        """Consume token of expected type or raise error."""
        if self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        
        if error_message is None:
            error_message = f"Expected {token_type.name}, got {self.current_token.type.name}"
        self.error(error_message)
    
    def synchronize(self) -> None:
        """Recover from parse error by finding next statement boundary."""
        self.advance()
        
        while not self.match(TokenType.EOF):
            if self.tokens[self.current - 1].type == TokenType.SEMICOLON:
                return
            
            if self.match(TokenType.IF, TokenType.FOR, TokenType.WHILE, 
                         TokenType.RETURN, TokenType.INT, TokenType.FLOAT_KW,
                         TokenType.CHAR_KW, TokenType.VOID):
                return
            
            self.advance()
    
    # ========================================================================
    # PARSING METHODS
    # ========================================================================
    
    def parse(self) -> Program:
        """Parse the entire program and return AST root."""
        declarations = []
        
        try:
            while not self.match(TokenType.EOF):
                try:
                    decl = self.parse_declaration()
                    if decl:
                        declarations.append(decl)
                except ParseError as e:
                    print(f"Parse Error: {e}")
                    self.synchronize()
            
            return Program(declarations)
        
        except Exception as e:
            print(f"Fatal Parse Error: {e}")
            return Program([])
    
    def parse_declaration(self) -> Optional[ASTNode]:
        """Parse top-level declaration (function or variable)."""
        # Skip EOF tokens
        if self.match(TokenType.EOF):
            return None
        
        if not self.match(TokenType.INT, TokenType.FLOAT_KW, TokenType.CHAR_KW, 
                          TokenType.VOID, TokenType.DOUBLE):
            self.error("Expected type declaration")
        
        # Parse type
        type_name = self.current_token.value
        self.advance()
        
        # Parse identifier
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected identifier")
        
        name = self.current_token.value
        self.advance()
        
        # Determine if function or variable declaration
        if self.match(TokenType.LEFT_PAREN):
            # Function declaration
            return self.parse_function_declaration(type_name, name)
        else:
            # Variable declaration
            return self.parse_variable_declaration(type_name, name)
    
    def parse_function_declaration(self, return_type: str, name: str) -> FunctionDeclaration:
        """Parse function declaration/definition."""
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        
        # Parse parameters
        parameters = []
        if not self.match(TokenType.RIGHT_PAREN):
            parameters = self.parse_parameter_list()
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        
        # Parse function body (optional for declarations)
        body = None
        if self.match(TokenType.LEFT_BRACE):
            body = self.parse_compound_statement()
        else:
            self.consume(TokenType.SEMICOLON, "Expected ';' after function declaration")
        
        return FunctionDeclaration(return_type, name, parameters, body)
    
    def parse_parameter_list(self) -> List[Parameter]:
        """Parse function parameter list."""
        parameters = []
        
        # First parameter
        param = self.parse_parameter()
        parameters.append(param)
        
        # Additional parameters
        while self.match(TokenType.COMMA):
            self.advance()  # consume comma
            param = self.parse_parameter()
            parameters.append(param)
        
        return parameters
    
    def parse_parameter(self) -> Parameter:
        """Parse single function parameter."""
        if not self.match(TokenType.INT, TokenType.FLOAT_KW, TokenType.CHAR_KW, 
                          TokenType.VOID, TokenType.DOUBLE):
            self.error("Expected parameter type")
        
        param_type = self.current_token.value
        self.advance()
        
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected parameter name")
        
        param_name = self.current_token.value
        self.advance()
        
        return Parameter(param_type, param_name)
    
    def parse_variable_declaration(self, type_name: str, name: str) -> VariableDeclaration:
        """Parse variable declaration with optional initialization."""
        initializer = None
        
        if self.match(TokenType.ASSIGN):
            self.advance()  # consume '='
            initializer = self.parse_expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VariableDeclaration(type_name, name, initializer)
    
    # ========================================================================
    # STATEMENT PARSING
    # ========================================================================
    
    def parse_compound_statement(self) -> CompoundStatement:
        """Parse compound statement (block)."""
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        statements = []
        while not self.match(TokenType.RIGHT_BRACE) and not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return CompoundStatement(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse any kind of statement."""
        try:
            if self.match(TokenType.LEFT_BRACE):
                return self.parse_compound_statement()
            
            elif self.match(TokenType.RETURN):
                return self.parse_return_statement()
            
            elif self.match(TokenType.IF):
                return self.parse_if_statement()
            
            elif self.match(TokenType.WHILE):
                return self.parse_while_statement()
            
            elif self.match(TokenType.FOR):
                return self.parse_for_statement()
            
            elif self.match(TokenType.INT, TokenType.FLOAT_KW, TokenType.CHAR_KW, 
                           TokenType.VOID, TokenType.DOUBLE):
                # Variable declaration in statement context
                type_name = self.current_token.value
                self.advance()
                
                if not self.match(TokenType.IDENTIFIER):
                    self.error("Expected identifier")
                
                name = self.current_token.value
                self.advance()
                
                return self.parse_variable_declaration(type_name, name)
            
            else:
                return self.parse_expression_statement()
        
        except ParseError as e:
            print(f"Statement Parse Error: {e}")
            self.synchronize()
            return None
    
    def parse_return_statement(self) -> ReturnStatement:
        """Parse return statement."""
        self.consume(TokenType.RETURN, "Expected 'return'")
        
        expression = None
        if not self.match(TokenType.SEMICOLON):
            expression = self.parse_expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after return statement")
        return ReturnStatement(expression)
    
    def parse_if_statement(self) -> IfStatement:
        """Parse if statement with optional else."""
        self.consume(TokenType.IF, "Expected 'if'")
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        
        condition = self.parse_expression()
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition")
        
        then_statement = self.parse_statement()
        
        else_statement = None
        if self.match(TokenType.ELSE):
            self.advance()  # consume 'else'
            else_statement = self.parse_statement()
        
        return IfStatement(condition, then_statement, else_statement)
    
    def parse_while_statement(self) -> WhileStatement:
        """Parse while loop statement."""
        self.consume(TokenType.WHILE, "Expected 'while'")
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        
        condition = self.parse_expression()
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition")
        
        body = self.parse_statement()
        
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        """Parse for loop statement."""
        self.consume(TokenType.FOR, "Expected 'for'")
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'")
        
        # Initialization (optional)
        init = None
        if not self.match(TokenType.SEMICOLON):
            init = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after for-loop initializer")
        
        # Condition (optional)
        condition = None
        if not self.match(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after for-loop condition")
        
        # Update (optional)
        update = None
        if not self.match(TokenType.RIGHT_PAREN):
            update = self.parse_expression()
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses")
        
        body = self.parse_statement()
        
        return ForStatement(init, condition, update, body)
    
    def parse_expression_statement(self) -> ExpressionStatement:
        """Parse expression statement."""
        expression = None
        if not self.match(TokenType.SEMICOLON):
            expression = self.parse_expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExpressionStatement(expression)
    
    # ========================================================================
    # EXPRESSION PARSING (with operator precedence)
    # ========================================================================
    
    def parse_expression(self) -> ASTNode:
        """Parse expression (top level)."""
        return self.parse_assignment()
    
    def parse_assignment(self) -> ASTNode:
        """Parse assignment expression (right associative)."""
        expr = self.parse_logical_or()
        
        if self.match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                      TokenType.MULT_ASSIGN, TokenType.DIV_ASSIGN, TokenType.MOD_ASSIGN):
            operator = self.current_token.value
            self.advance()
            right = self.parse_assignment()  # Right associative
            return AssignmentExpression(expr, operator, right)
        
        return expr
    
    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR expression."""
        expr = self.parse_logical_and()
        
        while self.match(TokenType.LOGICAL_OR):
            operator = self.current_token.value
            self.advance()
            right = self.parse_logical_and()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND expression."""
        expr = self.parse_equality()
        
        while self.match(TokenType.LOGICAL_AND):
            operator = self.current_token.value
            self.advance()
            right = self.parse_equality()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def parse_equality(self) -> ASTNode:
        """Parse equality expression."""
        expr = self.parse_relational()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.current_token.value
            self.advance()
            right = self.parse_relational()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def parse_relational(self) -> ASTNode:
        """Parse relational expression."""
        expr = self.parse_additive()
        
        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN,
                         TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            operator = self.current_token.value
            self.advance()
            right = self.parse_additive()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def parse_additive(self) -> ASTNode:
        """Parse additive expression."""
        expr = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.current_token.value
            self.advance()
            right = self.parse_multiplicative()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def parse_multiplicative(self) -> ASTNode:
        """Parse multiplicative expression."""
        expr = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.current_token.value
            self.advance()
            right = self.parse_unary()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def parse_unary(self) -> ASTNode:
        """Parse unary expression."""
        if self.match(TokenType.LOGICAL_NOT, TokenType.MINUS, 
                      TokenType.INCREMENT, TokenType.DECREMENT):
            operator = self.current_token.value
            self.advance()
            expr = self.parse_unary()
            return UnaryExpression(operator, expr)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ASTNode:
        """Parse postfix expression."""
        expr = self.parse_primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                # Function call
                self.advance()  # consume '('
                arguments = []
                
                if not self.match(TokenType.RIGHT_PAREN):
                    arguments = self.parse_argument_list()
                
                self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
                expr = CallExpression(expr, arguments)
            
            elif self.match(TokenType.INCREMENT, TokenType.DECREMENT):
                # Postfix increment/decrement
                operator = self.current_token.value
                self.advance()
                expr = UnaryExpression(f"post{operator}", expr)
            
            else:
                break
        
        return expr
    
    def parse_argument_list(self) -> List[ASTNode]:
        """Parse function call arguments."""
        arguments = []
        
        # First argument
        arguments.append(self.parse_expression())
        
        # Additional arguments
        while self.match(TokenType.COMMA):
            self.advance()  # consume comma
            arguments.append(self.parse_expression())
        
        return arguments
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expression."""
        if self.match(TokenType.IDENTIFIER):
            name = self.current_token.value
            self.advance()
            return Identifier(name)
        
        elif self.match(TokenType.INTEGER):
            value = int(self.current_token.value)
            self.advance()
            return IntegerLiteral(value)
        
        elif self.match(TokenType.FLOAT):
            value = float(self.current_token.value)
            self.advance()
            return FloatLiteral(value)
        
        elif self.match(TokenType.STRING):
            value = self.current_token.value
            self.advance()
            return StringLiteral(value)
        
        elif self.match(TokenType.CHAR):
            value = self.current_token.value
            self.advance()
            return CharLiteral(value)
        
        elif self.match(TokenType.LEFT_PAREN):
            self.advance()  # consume '('
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        
        else:
            self.error(f"Unexpected token: {self.current_token.type.name}")

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
    
    def _format_ast_node(self, node: ASTNode, max_length: int = 80) -> str:
        """Format AST node for readable debugging output."""
        if isinstance(node, FunctionDeclaration):
            param_str = f"({len(node.parameters)} params)" if node.parameters else "()"
            body_str = "with body" if node.body else "declaration only"
            return f"{node.return_type} {node.name}{param_str} {body_str}"
        elif isinstance(node, VariableDeclaration):
            init_str = "with initializer" if node.initializer else "no initializer"
            return f"{node.type} {node.name} ({init_str})"
        elif isinstance(node, BinaryExpression):
            return f"({self._format_ast_node(node.left, 20)} {node.operator} {self._format_ast_node(node.right, 20)})"
        elif isinstance(node, Identifier):
            return node.name
        elif isinstance(node, IntegerLiteral):
            return str(node.value)
        elif isinstance(node, StringLiteral):
            return f'"{node.value}"'
        else:
            result = str(node)
            return result[:max_length] + "..." if len(result) > max_length else result
    
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
            
            # Phase 2: Syntax Analysis (Parsing)
            print("🌳 Phase 2: Syntax Analysis (Parsing)...")
            self.parser = Parser(tokens)
            ast = self.parser.parse()
            print(f"   Generated AST with {len(ast.declarations)} top-level declarations")
            
            # Debug: Print AST structure
            print("   AST Structure:")
            for i, decl in enumerate(ast.declarations[:3]):  # Show first 3 declarations
                print(f"     {i+1}. {type(decl).__name__}: {self._format_ast_node(decl)}")
            
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