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
# SYMBOL TABLE AND TYPE SYSTEM
# ============================================================================

class CType:
    """Represents a C type with size and properties."""
    def __init__(self, name: str, size: int, is_signed: bool = True):
        self.name = name
        self.size = size  # Size in bytes
        self.is_signed = is_signed
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        if isinstance(other, CType):
            return self.name == other.name
        return False
    
    def is_compatible_with(self, other: 'CType') -> bool:
        """Check if this type is compatible with another for operations."""
        # Same type
        if self == other:
            return True
        
        # Numeric types can be promoted
        numeric_types = {'int', 'float', 'double', 'char'}
        if self.name in numeric_types and other.name in numeric_types:
            return True
        
        return False
    
    def can_assign_from(self, other: 'CType') -> bool:
        """Check if we can assign from other type to this type."""
        return self.is_compatible_with(other)

# Built-in C types
BUILTIN_TYPES = {
    'void': CType('void', 0, False),
    'char': CType('char', 1, True),
    'int': CType('int', 4, True),
    'float': CType('float', 4, True),
    'double': CType('double', 8, True),
}

@dataclass
class Symbol:
    """Represents a symbol in the symbol table."""
    name: str
    symbol_type: CType
    kind: str  # 'variable', 'function', 'parameter'
    scope_level: int
    is_defined: bool = False
    line: int = 0
    column: int = 0

class FunctionSymbol(Symbol):
    """Represents a function symbol with parameters and return type."""
    
    def __init__(self, name: str, return_type: CType, parameters: List[CType], 
                 scope_level: int, is_defined: bool = False, line: int = 0, column: int = 0):
        super().__init__(name, return_type, 'function', scope_level, is_defined, line, column)
        self.return_type = return_type
        self.parameters = parameters

class SymbolTable:
    """Symbol table with scope management."""
    
    def __init__(self):
        self.scopes = [{}]  # Stack of scopes (list of dictionaries)
        self.current_scope_level = 0
        
    def enter_scope(self):
        """Enter a new scope."""
        self.current_scope_level += 1
        self.scopes.append({})
    
    def exit_scope(self):
        """Exit current scope."""
        if self.current_scope_level > 0:
            self.scopes.pop()
            self.current_scope_level -= 1
    
    def declare_symbol(self, symbol: Symbol) -> bool:
        """Declare a symbol in current scope. Returns True if successful."""
        current_scope = self.scopes[self.current_scope_level]
        
        if symbol.name in current_scope:
            return False  # Already declared in this scope
        
        symbol.scope_level = self.current_scope_level
        current_scope[symbol.name] = symbol
        return True
    
    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        """Look up symbol in all scopes (from current to global)."""
        for scope_level in range(self.current_scope_level, -1, -1):
            scope = self.scopes[scope_level]
            if name in scope:
                return scope[name]
        return None
    
    def lookup_in_current_scope(self, name: str) -> Optional[Symbol]:
        """Look up symbol only in current scope."""
        current_scope = self.scopes[self.current_scope_level]
        return current_scope.get(name)

class SemanticError(Exception):
    """Exception raised during semantic analysis."""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Semantic Error: {message} at line {line}, column {column}")

# ============================================================================
# SEMANTIC ANALYZER
# ============================================================================

class SemanticAnalyzer:
    """
    Semantic Analyzer for C language.
    
    Performs:
    1. Symbol table management (scoping, declarations)
    2. Type checking (expressions, assignments, function calls)
    3. Semantic validation (undefined variables, type mismatches)
    4. Function signature validation
    5. Return statement checking
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function = None  # Track current function for return checking
        self.errors = []
        
        # Add built-in functions
        self._add_builtin_functions()
    
    def _add_builtin_functions(self):
        """Add built-in C functions to symbol table."""
        # printf function
        printf_symbol = FunctionSymbol(
            'printf', 
            BUILTIN_TYPES['int'], 
            [BUILTIN_TYPES['char']],  # Format string (simplified)
            0, 
            True
        )
        self.symbol_table.declare_symbol(printf_symbol)
    
    def error(self, message: str, line: int = 0, column: int = 0):
        """Record semantic error."""
        error = SemanticError(message, line, column)
        self.errors.append(error)
        print(f"Semantic Error: {message} at line {line}, column {column}")
    
    def analyze(self, ast: Program) -> bool:
        """Analyze the entire program. Returns True if no errors."""
        try:
            self.visit_program(ast)
            return len(self.errors) == 0
        except Exception as e:
            self.error(f"Fatal semantic analysis error: {e}")
            return False
    
    def visit_program(self, node: Program):
        """Visit program root node."""
        print("🔍 Analyzing program structure...")
        
        # First pass: Declare all functions and global variables
        for declaration in node.declarations:
            if isinstance(declaration, FunctionDeclaration):
                self._declare_function(declaration)
            elif isinstance(declaration, VariableDeclaration):
                self._declare_global_variable(declaration)
        
        # Second pass: Analyze function bodies
        for declaration in node.declarations:
            if isinstance(declaration, FunctionDeclaration) and declaration.body:
                self.visit_function_declaration(declaration)
        
        print(f"   Found {len([d for d in node.declarations if isinstance(d, FunctionDeclaration)])} functions")
        print(f"   Found {len([d for d in node.declarations if isinstance(d, VariableDeclaration)])} global variables")
    
    def _declare_function(self, node: FunctionDeclaration):
        """Declare function in symbol table."""
        # Get return type
        return_type = BUILTIN_TYPES.get(node.return_type)
        if not return_type:
            self.error(f"Unknown return type: {node.return_type}")
            return
        
        # Get parameter types
        param_types = []
        for param in node.parameters:
            param_type = BUILTIN_TYPES.get(param.type)
            if not param_type:
                self.error(f"Unknown parameter type: {param.type}")
                continue
            param_types.append(param_type)
        
        # Create function symbol
        func_symbol = FunctionSymbol(
            node.name,
            return_type,
            param_types,
            0,  # Global scope
            node.body is not None  # Defined if has body
        )
        
        if not self.symbol_table.declare_symbol(func_symbol):
            self.error(f"Function '{node.name}' already declared")
    
    def _declare_global_variable(self, node: VariableDeclaration):
        """Declare global variable in symbol table."""
        var_type = BUILTIN_TYPES.get(node.type)
        if not var_type:
            self.error(f"Unknown variable type: {node.type}")
            return
        
        var_symbol = Symbol(
            node.name,
            var_type,
            'variable',
            0,  # Global scope
            node.initializer is not None
        )
        
        if not self.symbol_table.declare_symbol(var_symbol):
            self.error(f"Global variable '{node.name}' already declared")
        
        # Check initializer type if present
        if node.initializer:
            init_type = self.visit_expression(node.initializer)
            if init_type and not var_type.can_assign_from(init_type):
                self.error(f"Cannot assign {init_type} to {var_type}")
    
    def visit_function_declaration(self, node: FunctionDeclaration):
        """Visit function declaration with body."""
        print(f"   Analyzing function: {node.name}")
        
        # Set current function for return checking
        func_symbol = self.symbol_table.lookup_symbol(node.name)
        self.current_function = func_symbol
        
        # Enter function scope
        self.symbol_table.enter_scope()
        
        # Declare parameters in function scope
        for param in node.parameters:
            param_type = BUILTIN_TYPES.get(param.type)
            if param_type:
                param_symbol = Symbol(param.name, param_type, 'parameter', 
                                    self.symbol_table.current_scope_level, True)
                if not self.symbol_table.declare_symbol(param_symbol):
                    self.error(f"Parameter '{param.name}' already declared")
        
        # Analyze function body
        if node.body:
            self.visit_compound_statement(node.body)
        
        # Exit function scope
        self.symbol_table.exit_scope()
        self.current_function = None
    
    def visit_compound_statement(self, node: CompoundStatement):
        """Visit compound statement (block)."""
        self.symbol_table.enter_scope()
        
        for statement in node.statements:
            self.visit_statement(statement)
        
        self.symbol_table.exit_scope()
    
    def visit_statement(self, node: ASTNode):
        """Visit any statement."""
        if isinstance(node, VariableDeclaration):
            self.visit_variable_declaration(node)
        elif isinstance(node, ExpressionStatement):
            if node.expression:
                self.visit_expression(node.expression)
        elif isinstance(node, ReturnStatement):
            self.visit_return_statement(node)
        elif isinstance(node, IfStatement):
            self.visit_if_statement(node)
        elif isinstance(node, WhileStatement):
            self.visit_while_statement(node)
        elif isinstance(node, ForStatement):
            self.visit_for_statement(node)
        elif isinstance(node, CompoundStatement):
            self.visit_compound_statement(node)
    
    def visit_variable_declaration(self, node: VariableDeclaration):
        """Visit variable declaration."""
        var_type = BUILTIN_TYPES.get(node.type)
        if not var_type:
            self.error(f"Unknown variable type: {node.type}")
            return
        
        var_symbol = Symbol(
            node.name,
            var_type,
            'variable',
            self.symbol_table.current_scope_level,
            node.initializer is not None
        )
        
        if not self.symbol_table.declare_symbol(var_symbol):
            self.error(f"Variable '{node.name}' already declared in this scope")
        
        # Check initializer type
        if node.initializer:
            init_type = self.visit_expression(node.initializer)
            if init_type and not var_type.can_assign_from(init_type):
                self.error(f"Cannot assign {init_type} to {var_type}")
    
    def visit_return_statement(self, node: ReturnStatement):
        """Visit return statement."""
        if not self.current_function:
            self.error("Return statement outside function")
            return
        
        expected_type = self.current_function.return_type
        
        if node.expression:
            actual_type = self.visit_expression(node.expression)
            if actual_type and not expected_type.can_assign_from(actual_type):
                self.error(f"Cannot return {actual_type} from function returning {expected_type}")
        else:
            if expected_type.name != 'void':
                self.error(f"Function returning {expected_type} must return a value")
    
    def visit_if_statement(self, node: IfStatement):
        """Visit if statement."""
        # Check condition type
        condition_type = self.visit_expression(node.condition)
        # In C, any non-zero value is true, so we're lenient here
        
        # Visit then statement
        self.visit_statement(node.then_statement)
        
        # Visit else statement if present
        if node.else_statement:
            self.visit_statement(node.else_statement)
    
    def visit_while_statement(self, node: WhileStatement):
        """Visit while statement."""
        # Check condition type
        condition_type = self.visit_expression(node.condition)
        
        # Visit body
        self.visit_statement(node.body)
    
    def visit_for_statement(self, node: ForStatement):
        """Visit for statement."""
        # Visit initialization
        if node.init:
            self.visit_expression(node.init)
        
        # Visit condition
        if node.condition:
            self.visit_expression(node.condition)
        
        # Visit update
        if node.update:
            self.visit_expression(node.update)
        
        # Visit body
        self.visit_statement(node.body)
    
    def visit_expression(self, node: ASTNode) -> Optional[CType]:
        """Visit expression and return its type."""
        if isinstance(node, IntegerLiteral):
            return BUILTIN_TYPES['int']
        
        elif isinstance(node, FloatLiteral):
            return BUILTIN_TYPES['float']
        
        elif isinstance(node, StringLiteral):
            return BUILTIN_TYPES['char']  # char* in reality
        
        elif isinstance(node, CharLiteral):
            return BUILTIN_TYPES['char']
        
        elif isinstance(node, Identifier):
            symbol = self.symbol_table.lookup_symbol(node.name)
            if not symbol:
                self.error(f"Undefined variable: {node.name}")
                return None
            return symbol.symbol_type
        
        elif isinstance(node, BinaryExpression):
            return self.visit_binary_expression(node)
        
        elif isinstance(node, UnaryExpression):
            return self.visit_unary_expression(node)
        
        elif isinstance(node, AssignmentExpression):
            return self.visit_assignment_expression(node)
        
        elif isinstance(node, CallExpression):
            return self.visit_call_expression(node)
        
        return None
    
    def visit_binary_expression(self, node: BinaryExpression) -> Optional[CType]:
        """Visit binary expression and return result type."""
        left_type = self.visit_expression(node.left)
        right_type = self.visit_expression(node.right)
        
        if not left_type or not right_type:
            return None
        
        # Arithmetic operators
        if node.operator in ['+', '-', '*', '/', '%']:
            if left_type.is_compatible_with(right_type):
                # Type promotion: if either is float, result is float
                if left_type.name == 'float' or right_type.name == 'float':
                    return BUILTIN_TYPES['float']
                return BUILTIN_TYPES['int']
            else:
                self.error(f"Cannot perform {node.operator} on {left_type} and {right_type}")
                return None
        
        # Comparison operators
        elif node.operator in ['<', '>', '<=', '>=', '==', '!=']:
            if left_type.is_compatible_with(right_type):
                return BUILTIN_TYPES['int']  # Boolean result as int
            else:
                self.error(f"Cannot compare {left_type} and {right_type}")
                return None
        
        # Logical operators
        elif node.operator in ['&&', '||']:
            return BUILTIN_TYPES['int']  # Boolean result as int
        
        return None
    
    def visit_unary_expression(self, node: UnaryExpression) -> Optional[CType]:
        """Visit unary expression and return result type."""
        operand_type = self.visit_expression(node.operand)
        
        if not operand_type:
            return None
        
        if node.operator in ['-', '!', '++', '--']:
            return operand_type
        
        return None
    
    def visit_assignment_expression(self, node: AssignmentExpression) -> Optional[CType]:
        """Visit assignment expression and return result type."""
        left_type = self.visit_expression(node.left)
        right_type = self.visit_expression(node.right)
        
        if not left_type or not right_type:
            return None
        
        # Check if assignment is valid
        if node.operator == '=':
            if not left_type.can_assign_from(right_type):
                self.error(f"Cannot assign {right_type} to {left_type}")
                return None
        else:
            # Compound assignment (+=, -=, etc.)
            if not left_type.is_compatible_with(right_type):
                self.error(f"Cannot perform {node.operator} with {left_type} and {right_type}")
                return None
        
        return left_type
    
    def visit_call_expression(self, node: CallExpression) -> Optional[CType]:
        """Visit function call expression and return result type."""
        # Get function name
        if not isinstance(node.function, Identifier):
            self.error("Invalid function call")
            return None
        
        func_name = node.function.name
        func_symbol = self.symbol_table.lookup_symbol(func_name)
        
        if not func_symbol:
            self.error(f"Undefined function: {func_name}")
            return None
        
        if not isinstance(func_symbol, FunctionSymbol):
            self.error(f"'{func_name}' is not a function")
            return None
        
        # Check argument count
        if len(node.arguments) != len(func_symbol.parameters):
            self.error(f"Function '{func_name}' expects {len(func_symbol.parameters)} arguments, got {len(node.arguments)}")
            return None
        
        # Check argument types
        for i, (arg, expected_type) in enumerate(zip(node.arguments, func_symbol.parameters)):
            actual_type = self.visit_expression(arg)
            if actual_type and not expected_type.can_assign_from(actual_type):
                self.error(f"Argument {i+1} to '{func_name}': cannot convert {actual_type} to {expected_type}")
        
        return func_symbol.return_type

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
            
            # Phase 3: Semantic Analysis
            print("🔍 Phase 3: Semantic Analysis...")
            self.semantic_analyzer = SemanticAnalyzer()
            semantic_success = self.semantic_analyzer.analyze(ast)
            
            if not semantic_success:
                print(f"   ❌ Found {len(self.semantic_analyzer.errors)} semantic errors:")
                for error in self.semantic_analyzer.errors:
                    print(f"     • {error.message}")
                return False
            
            print("   ✅ Semantic analysis completed successfully!")
            
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