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
from typing import List, Dict, Optional, Union, Any, Set
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
# CODE GENERATOR (x86-64 ASSEMBLY)
# ============================================================================

class Register:
    """Represents an x86-64 register."""
    def __init__(self, name: str, size: int = 64):
        self.name = name
        self.size = size  # 8, 16, 32, or 64 bits
        self.is_used = False
    
    def __str__(self):
        return f"%{self.name}"
    
    def get_size_variant(self, size: int) -> str:
        """Get register name for specific size."""
        if self.name in ["rax", "eax", "ax", "al"]:
            if size == 64: return "rax"
            elif size == 32: return "eax"
            elif size == 16: return "ax"
            elif size == 8: return "al"
        elif self.name in ["rbx", "ebx", "bx", "bl"]:
            if size == 64: return "rbx"
            elif size == 32: return "ebx"
            elif size == 16: return "bx"
            elif size == 8: return "bl"
        elif self.name in ["rcx", "ecx", "cx", "cl"]:
            if size == 64: return "rcx"
            elif size == 32: return "ecx"
            elif size == 16: return "cx"
            elif size == 8: return "cl"
        elif self.name in ["rdx", "edx", "dx", "dl"]:
            if size == 64: return "rdx"
            elif size == 32: return "edx"
            elif size == 16: return "dx"
            elif size == 8: return "dl"
        # Add more registers as needed
        return self.name

class RegisterAllocator:
    """Simple register allocator for code generation."""
    
    def __init__(self):
        self.registers = {
            'rax': Register('rax'),
            'rbx': Register('rbx'),
            'rcx': Register('rcx'),
            'rdx': Register('rdx'),
            'rsi': Register('rsi'),
            'rdi': Register('rdi'),
            'r8': Register('r8'),
            'r9': Register('r9'),
            'r10': Register('r10'),
            'r11': Register('r11'),
        }
        
        # Calling convention registers
        self.param_registers = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        self.return_register = 'rax'
        
        # Stack management
        self.stack_offset = 0
        self.local_vars = {}  # Maps variable names to stack offsets
        
    def allocate_register(self) -> Optional[str]:
        """Allocate an available register."""
        for name, reg in self.registers.items():
            if not reg.is_used and name not in ['rsp', 'rbp']:
                reg.is_used = True
                return name
        return None
    
    def free_register(self, name: str):
        """Free a register for reuse."""
        if name in self.registers:
            self.registers[name].is_used = False
    
    def get_param_register(self, index: int) -> Optional[str]:
        """Get register for function parameter by index."""
        if 0 <= index < len(self.param_registers):
            return self.param_registers[index]
        return None
    
    def allocate_stack_space(self, var_name: str, size: int = 8) -> int:
        """Allocate space on stack for local variable."""
        self.stack_offset += size
        self.local_vars[var_name] = self.stack_offset
        return self.stack_offset

class CodeGenerator:
    """
    x86-64 Assembly Code Generator for C programs.
    
    Generates GNU assembler (GAS) syntax assembly code from validated AST.
    Supports:
    - Function declarations and calls
    - Variable declarations and access
    - Arithmetic and logical expressions
    - Control flow (if/while/for statements)
    - Stack management and calling conventions
    """
    
    def __init__(self):
        self.output = []  # Generated assembly code lines
        self.register_allocator = RegisterAllocator()
        self.advanced_allocator = AdvancedRegisterAllocator()
        self.label_counter = 0
        self.current_function = None
        self.use_advanced_allocation = True  # Enable advanced register allocation
    
    def set_advanced_allocation(self, enabled: bool):
        """Enable or disable advanced register allocation."""
        self.use_advanced_allocation = enabled
        
    def generate_label(self, prefix: str = "L") -> str:
        """Generate unique label for jumps and branches."""
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"
    
    def emit(self, instruction: str, comment: str = ""):
        """Emit assembly instruction with optional comment."""
        if comment:
            self.output.append(f"    {instruction:<30} # {comment}")
        else:
            self.output.append(f"    {instruction}")
    
    def emit_label(self, label: str):
        """Emit assembly label."""
        self.output.append(f"{label}:")
    
    def emit_directive(self, directive: str):
        """Emit assembler directive."""
        self.output.append(directive)
    
    def generate(self, ast: Program) -> str:
        """Generate complete assembly program from AST."""
        print("⚙️ Generating x86-64 assembly code...")
        
        # Emit program header
        self.emit_directive(".section .text")
        self.emit_directive(".global _start")
        
        # Generate code for all declarations
        for declaration in ast.declarations:
            self.generate_declaration(declaration)
        
        # Add program entry point if no main function
        if not any(isinstance(d, FunctionDeclaration) and d.name == "main" 
                  for d in ast.declarations):
            self.emit_directive("")
            self.emit_label("_start")
            self.emit("mov $60, %rax", "exit syscall")
            self.emit("mov $0, %rdi", "exit status")
            self.emit("syscall", "invoke system call")
        
        # Join all output lines
        return "\n".join(self.output)
    
    def generate_declaration(self, node: ASTNode):
        """Generate code for top-level declaration."""
        if isinstance(node, FunctionDeclaration):
            self.generate_function(node)
        elif isinstance(node, VariableDeclaration):
            self.generate_global_variable(node)
    
    def generate_global_variable(self, node: VariableDeclaration):
        """Generate code for global variable declaration."""
        self.emit_directive(".section .data")
        if node.initializer:
            if isinstance(node.initializer, IntegerLiteral):
                self.emit_directive(f"{node.name}: .quad {node.initializer.value}")
            else:
                self.emit_directive(f"{node.name}: .quad 0")
        else:
            self.emit_directive(f"{node.name}: .quad 0")
        self.emit_directive(".section .text")
    
    def generate_function(self, node: FunctionDeclaration):
        """Generate code for function declaration."""
        if not node.body:
            return  # Skip function declarations without bodies
        
        print(f"   Generating function: {node.name}")
        self.current_function = node
        
        # Perform advanced register allocation if enabled
        if self.use_advanced_allocation:
            self.allocation_map = self.advanced_allocator.allocate_registers(node)
        else:
            # Reset simple register allocator for new function
            self.register_allocator = RegisterAllocator()
            self.allocation_map = {}
        
        # Function label
        self.emit_directive("")
        if node.name == "main":
            self.emit_label("_start")
        else:
            self.emit_label(node.name)
        
        # Function prologue
        self.emit("pushq %rbp", "save old base pointer")
        self.emit("movq %rsp, %rbp", "establish new base pointer")
        
        # Allocate space for local variables (simplified)
        local_space = len([stmt for stmt in self.collect_local_vars(node.body)]) * 8
        if local_space > 0:
            self.emit(f"subq ${local_space}, %rsp", "allocate local variable space")
        
        # Store parameters in local variables
        for i, param in enumerate(node.parameters):
            param_reg = self.register_allocator.get_param_register(i)
            if param_reg:
                offset = self.register_allocator.allocate_stack_space(param.name)
                self.emit(f"movq %{param_reg}, -{offset}(%rbp)", f"store parameter {param.name}")
        
        # Generate function body
        self.generate_statement(node.body)
        
        # Function epilogue (in case no return statement)
        self.generate_function_epilogue(node.name)
    
    def collect_local_vars(self, node: ASTNode) -> List[str]:
        """Collect all local variable names for stack allocation."""
        vars_list = []
        if isinstance(node, CompoundStatement):
            for stmt in node.statements:
                if isinstance(stmt, VariableDeclaration):
                    vars_list.append(stmt.name)
                vars_list.extend(self.collect_local_vars(stmt))
        elif isinstance(node, IfStatement):
            vars_list.extend(self.collect_local_vars(node.then_statement))
            if node.else_statement:
                vars_list.extend(self.collect_local_vars(node.else_statement))
        elif isinstance(node, WhileStatement):
            vars_list.extend(self.collect_local_vars(node.body))
        # Add more statement types as needed
        return vars_list
    
    def generate_function_epilogue(self, func_name: str):
        """Generate function epilogue and return."""
        self.emit_label(f"{func_name}_epilogue")
        
        if func_name == "main":
            # Main function - exit program
            self.emit("mov $60, %rax", "exit syscall")
            self.emit("mov $0, %rdi", "exit status 0")
            self.emit("syscall", "invoke system call")
        else:
            # Regular function return
            self.emit("movq %rbp, %rsp", "restore stack pointer")
            self.emit("popq %rbp", "restore old base pointer")
            self.emit("ret", "return to caller")
    
    def generate_statement(self, node: ASTNode):
        """Generate code for any statement."""
        if isinstance(node, CompoundStatement):
            for stmt in node.statements:
                self.generate_statement(stmt)
        
        elif isinstance(node, VariableDeclaration):
            self.generate_variable_declaration(node)
        
        elif isinstance(node, ExpressionStatement):
            if node.expression:
                self.generate_expression(node.expression)
        
        elif isinstance(node, ReturnStatement):
            self.generate_return_statement(node)
        
        elif isinstance(node, IfStatement):
            self.generate_if_statement(node)
        
        elif isinstance(node, WhileStatement):
            self.generate_while_statement(node)
        
        # Add more statement types as needed
    
    def generate_variable_declaration(self, node: VariableDeclaration):
        """Generate code for local variable declaration."""
        # Allocate stack space
        offset = self.register_allocator.allocate_stack_space(node.name)
        
        if node.initializer:
            # Generate code for initializer and store result
            result_reg = self.generate_expression(node.initializer)
            if result_reg:
                self.emit(f"movq %{result_reg}, -{offset}(%rbp)", f"store {node.name}")
                self.register_allocator.free_register(result_reg)
    
    def generate_return_statement(self, node: ReturnStatement):
        """Generate code for return statement."""
        if node.expression:
            # Generate expression and move result to return register
            result_reg = self.generate_expression(node.expression)
            if result_reg and result_reg != 'rax':
                self.emit(f"movq %{result_reg}, %rax", "move return value to rax")
                self.register_allocator.free_register(result_reg)
        
        # Jump to function epilogue
        if self.current_function:
            self.emit(f"jmp {self.current_function.name}_epilogue", "return from function")
    
    def generate_if_statement(self, node: IfStatement):
        """Generate code for if statement."""
        else_label = self.generate_label("else")
        end_label = self.generate_label("end_if")
        
        # Generate condition
        cond_reg = self.generate_expression(node.condition)
        if cond_reg:
            self.emit(f"testq %{cond_reg}, %{cond_reg}", "test condition")
            self.emit(f"jz {else_label}", "jump if false")
            self.register_allocator.free_register(cond_reg)
        
        # Generate then statement
        self.generate_statement(node.then_statement)
        self.emit(f"jmp {end_label}", "skip else part")
        
        # Generate else statement
        self.emit_label(else_label)
        if node.else_statement:
            self.generate_statement(node.else_statement)
        
        self.emit_label(end_label)
    
    def generate_while_statement(self, node: WhileStatement):
        """Generate code for while loop."""
        loop_start = self.generate_label("while_start")
        loop_end = self.generate_label("while_end")
        
        # Loop start
        self.emit_label(loop_start)
        
        # Generate condition
        cond_reg = self.generate_expression(node.condition)
        if cond_reg:
            self.emit(f"testq %{cond_reg}, %{cond_reg}", "test loop condition")
            self.emit(f"jz {loop_end}", "exit if false")
            self.register_allocator.free_register(cond_reg)
        
        # Generate body
        self.generate_statement(node.body)
        
        # Jump back to condition
        self.emit(f"jmp {loop_start}", "repeat loop")
        
        # Loop end
        self.emit_label(loop_end)
    
    def generate_expression(self, node: ASTNode) -> Optional[str]:
        """Generate code for expression and return register containing result."""
        if isinstance(node, IntegerLiteral):
            reg = self.register_allocator.allocate_register()
            if reg:
                self.emit(f"movq ${node.value}, %{reg}", f"load integer {node.value}")
            return reg
        
        elif isinstance(node, Identifier):
            # Use advanced register allocation if available
            if self.use_advanced_allocation and node.name in self.allocation_map:
                allocated_location = self.allocation_map[node.name]
                if allocated_location == 'spilled':
                    # Variable is spilled to stack
                    offset = self.advanced_allocator.spilled_variables[node.name]
                    reg = self.register_allocator.allocate_register()
                    if reg:
                        self.emit(f"movq -{offset}(%rbp), %{reg}", f"load spilled {node.name}")
                    return reg
                else:
                    # Variable is in register
                    return allocated_location
            
            # Fallback to original method
            elif node.name in self.register_allocator.local_vars:
                offset = self.register_allocator.local_vars[node.name]
                reg = self.register_allocator.allocate_register()
                if reg:
                    self.emit(f"movq -{offset}(%rbp), %{reg}", f"load {node.name}")
                return reg
            else:
                # Global variable
                reg = self.register_allocator.allocate_register()
                if reg:
                    self.emit(f"movq {node.name}(%rip), %{reg}", f"load global {node.name}")
                return reg
        
        elif isinstance(node, BinaryExpression):
            return self.generate_binary_expression(node)
        
        elif isinstance(node, AssignmentExpression):
            return self.generate_assignment_expression(node)
        
        elif isinstance(node, CallExpression):
            return self.generate_call_expression(node)
        
        return None
    
    def generate_binary_expression(self, node: BinaryExpression) -> Optional[str]:
        """Generate code for binary expression."""
        # Generate left operand
        left_reg = self.generate_expression(node.left)
        
        # Generate right operand
        right_reg = self.generate_expression(node.right)
        
        if not left_reg or not right_reg:
            return None
        
        # Perform operation
        if node.operator == '+':
            self.emit(f"addq %{right_reg}, %{left_reg}", "add operation")
        elif node.operator == '-':
            self.emit(f"subq %{right_reg}, %{left_reg}", "subtract operation")
        elif node.operator == '*':
            self.emit(f"imulq %{right_reg}, %{left_reg}", "multiply operation")
        elif node.operator == '<':
            self.emit(f"cmpq %{right_reg}, %{left_reg}", "compare for less than")
            self.emit(f"setl %al", "set result of comparison")
            self.emit(f"movzbq %al, %{left_reg}", "zero-extend result")
        elif node.operator == '>':
            self.emit(f"cmpq %{right_reg}, %{left_reg}", "compare for greater than")
            self.emit(f"setg %al", "set result of comparison")
            self.emit(f"movzbq %al, %{left_reg}", "zero-extend result")
        # Add more operators as needed
        
        # Free right register, return left register with result
        self.register_allocator.free_register(right_reg)
        return left_reg
    
    def generate_assignment_expression(self, node: AssignmentExpression) -> Optional[str]:
        """Generate code for assignment expression."""
        if not isinstance(node.left, Identifier):
            return None
        
        var_name = node.left.name
        
        # Generate right-hand side
        rhs_reg = self.generate_expression(node.right)
        if not rhs_reg:
            return None
        
        # Store to variable using advanced allocation if available
        if self.use_advanced_allocation and var_name in self.allocation_map:
            allocated_location = self.allocation_map[var_name]
            if allocated_location == 'spilled':
                # Variable is spilled to stack
                offset = self.advanced_allocator.spilled_variables[var_name]
                self.emit(f"movq %{rhs_reg}, -{offset}(%rbp)", f"assign to spilled {var_name}")
            else:
                # Variable is in register - direct register-to-register move
                if rhs_reg != allocated_location:
                    self.emit(f"movq %{rhs_reg}, %{allocated_location}", f"assign to {var_name}")
        elif var_name in self.register_allocator.local_vars:
            offset = self.register_allocator.local_vars[var_name]
            self.emit(f"movq %{rhs_reg}, -{offset}(%rbp)", f"assign to {var_name}")
        else:
            # Global variable
            self.emit(f"movq %{rhs_reg}, {var_name}(%rip)", f"assign to global {var_name}")
        
        return rhs_reg
    
    def generate_call_expression(self, node: CallExpression) -> Optional[str]:
        """Generate code for function call."""
        if not isinstance(node.function, Identifier):
            return None
        
        func_name = node.function.name
        
        # Generate arguments and place in parameter registers
        for i, arg in enumerate(node.arguments):
            arg_reg = self.generate_expression(arg)
            param_reg = self.register_allocator.get_param_register(i)
            
            if arg_reg and param_reg and arg_reg != param_reg:
                self.emit(f"movq %{arg_reg}, %{param_reg}", f"pass argument {i}")
                self.register_allocator.free_register(arg_reg)
        
        # Call function
        self.emit(f"call {func_name}", f"call function {func_name}")
        
        # Return value is in rax
        return 'rax'

# ============================================================================
# OPTIMIZATION PASSES
# ============================================================================

class OptimizationPass:
    """Base class for optimization passes."""
    
    def __init__(self, name: str):
        self.name = name
        self.optimizations_applied = 0
    
    def optimize(self, node: ASTNode) -> ASTNode:
        """Apply optimization to AST node. Override in subclasses."""
        return node
    
    def report(self):
        """Report optimization statistics."""
        print(f"   {self.name}: {self.optimizations_applied} optimizations applied")

class ConstantFoldingPass(OptimizationPass):
    """
    Constant Folding Optimization Pass
    
    Evaluates constant expressions at compile time:
    - 2 + 3 → 5
    - 10 * 0 → 0  
    - x + 0 → x
    - x * 1 → x
    """
    
    def __init__(self):
        super().__init__("Constant Folding")
    
    def optimize(self, node: ASTNode) -> ASTNode:
        """Apply constant folding to AST."""
        if isinstance(node, Program):
            # Optimize all declarations in the program
            optimized_declarations = []
            for declaration in node.declarations:
                optimized_declarations.append(self.fold_constants(declaration))
            return Program(optimized_declarations)
        else:
            return self.fold_constants(node)
    
    def fold_constants(self, node: ASTNode) -> ASTNode:
        """Recursively fold constant expressions."""
        if isinstance(node, BinaryExpression):
            return self.fold_binary_expression(node)
        elif isinstance(node, UnaryExpression):
            return self.fold_unary_expression(node)
        elif isinstance(node, FunctionDeclaration):
            if node.body:
                node.body = self.fold_constants(node.body)
        elif isinstance(node, CompoundStatement):
            node.statements = [self.fold_constants(stmt) for stmt in node.statements]
        elif isinstance(node, IfStatement):
            node.condition = self.fold_constants(node.condition)
            node.then_statement = self.fold_constants(node.then_statement)
            if node.else_statement:
                node.else_statement = self.fold_constants(node.else_statement)
        elif isinstance(node, WhileStatement):
            node.condition = self.fold_constants(node.condition)
            node.body = self.fold_constants(node.body)
        elif isinstance(node, ReturnStatement):
            if node.expression:
                node.expression = self.fold_constants(node.expression)
        elif isinstance(node, VariableDeclaration):
            if node.initializer:
                node.initializer = self.fold_constants(node.initializer)
        elif isinstance(node, ExpressionStatement):
            if node.expression:
                node.expression = self.fold_constants(node.expression)
        elif isinstance(node, AssignmentExpression):
            node.right = self.fold_constants(node.right)
        elif isinstance(node, CallExpression):
            node.arguments = [self.fold_constants(arg) for arg in node.arguments]
        
        return node
    
    def fold_binary_expression(self, node: BinaryExpression) -> ASTNode:
        """Fold binary expressions with constant operands."""
        # Recursively fold operands first
        left = self.fold_constants(node.left)
        right = self.fold_constants(node.right)
        
        # Check if both operands are integer literals
        if isinstance(left, IntegerLiteral) and isinstance(right, IntegerLiteral):
            result = self.evaluate_binary_operation(left.value, node.operator, right.value)
            if result is not None:
                self.optimizations_applied += 1
                return IntegerLiteral(result)
        
        # Algebraic simplifications
        optimized = self.apply_algebraic_simplifications(left, node.operator, right)
        if optimized:
            return optimized
        
        # Return updated expression
        return BinaryExpression(left, node.operator, right)
    
    def evaluate_binary_operation(self, left_val: int, operator: str, right_val: int) -> Optional[int]:
        """Evaluate binary operation on constant values."""
        try:
            if operator == '+':
                return left_val + right_val
            elif operator == '-':
                return left_val - right_val
            elif operator == '*':
                return left_val * right_val
            elif operator == '/':
                return left_val // right_val if right_val != 0 else None
            elif operator == '%':
                return left_val % right_val if right_val != 0 else None
            elif operator == '<':
                return 1 if left_val < right_val else 0
            elif operator == '>':
                return 1 if left_val > right_val else 0
            elif operator == '<=':
                return 1 if left_val <= right_val else 0
            elif operator == '>=':
                return 1 if left_val >= right_val else 0
            elif operator == '==':
                return 1 if left_val == right_val else 0
            elif operator == '!=':
                return 1 if left_val != right_val else 0
            elif operator == '&&':
                return 1 if left_val and right_val else 0
            elif operator == '||':
                return 1 if left_val or right_val else 0
        except (ZeroDivisionError, ValueError):
            return None
        return None
    
    def apply_algebraic_simplifications(self, left: ASTNode, operator: str, right: ASTNode) -> Optional[ASTNode]:
        """Apply algebraic simplification rules."""
        # x + 0 → x
        if operator == '+':
            if isinstance(right, IntegerLiteral) and right.value == 0:
                self.optimizations_applied += 1
                return left
            if isinstance(left, IntegerLiteral) and left.value == 0:
                self.optimizations_applied += 1
                return right
        
        # x - 0 → x
        elif operator == '-':
            if isinstance(right, IntegerLiteral) and right.value == 0:
                self.optimizations_applied += 1
                return left
        
        # x * 1 → x, x * 0 → 0
        elif operator == '*':
            if isinstance(right, IntegerLiteral):
                if right.value == 1:
                    self.optimizations_applied += 1
                    return left
                elif right.value == 0:
                    self.optimizations_applied += 1
                    return IntegerLiteral(0)
            if isinstance(left, IntegerLiteral):
                if left.value == 1:
                    self.optimizations_applied += 1
                    return right
                elif left.value == 0:
                    self.optimizations_applied += 1
                    return IntegerLiteral(0)
        
        # x / 1 → x
        elif operator == '/':
            if isinstance(right, IntegerLiteral) and right.value == 1:
                self.optimizations_applied += 1
                return left
        
        return None
    
    def fold_unary_expression(self, node: UnaryExpression) -> ASTNode:
        """Fold unary expressions with constant operands."""
        operand = self.fold_constants(node.operand)
        
        if isinstance(operand, IntegerLiteral):
            if node.operator == '-':
                self.optimizations_applied += 1
                return IntegerLiteral(-operand.value)
            elif node.operator == '!':
                self.optimizations_applied += 1
                return IntegerLiteral(1 if operand.value == 0 else 0)
        
        return UnaryExpression(node.operator, operand)

class DeadCodeEliminationPass(OptimizationPass):
    """
    Dead Code Elimination Optimization Pass
    
    Removes unreachable and unused code:
    - Statements after return statements
    - If statements with constant false conditions
    - Unused variable declarations
    """
    
    def __init__(self):
        super().__init__("Dead Code Elimination")
    
    def optimize(self, node: ASTNode) -> ASTNode:
        """Apply dead code elimination to AST."""
        if isinstance(node, Program):
            optimized_declarations = []
            for declaration in node.declarations:
                optimized_declarations.append(self.eliminate_dead_code(declaration))
            return Program(optimized_declarations)
        else:
            return self.eliminate_dead_code(node)
    
    def eliminate_dead_code(self, node: ASTNode) -> ASTNode:
        """Recursively eliminate dead code."""
        if isinstance(node, CompoundStatement):
            return self.eliminate_dead_statements(node)
        elif isinstance(node, IfStatement):
            return self.eliminate_dead_if(node)
        elif isinstance(node, FunctionDeclaration):
            if node.body:
                node.body = self.eliminate_dead_code(node.body)
        elif isinstance(node, WhileStatement):
            node.condition = self.eliminate_dead_code(node.condition)
            node.body = self.eliminate_dead_code(node.body)
        
        return node
    
    def eliminate_dead_statements(self, node: CompoundStatement) -> CompoundStatement:
        """Remove statements after return statements."""
        new_statements = []
        found_return = False
        
        for stmt in node.statements:
            if found_return:
                # This statement is unreachable
                self.optimizations_applied += 1
                continue
            
            # Recursively process statement
            processed_stmt = self.eliminate_dead_code(stmt)
            new_statements.append(processed_stmt)
            
            # Check if this statement is a return
            if isinstance(processed_stmt, ReturnStatement):
                found_return = True
        
        return CompoundStatement(new_statements)
    
    def eliminate_dead_if(self, node: IfStatement) -> ASTNode:
        """Eliminate if statements with constant conditions."""
        # Process condition
        condition = self.eliminate_dead_code(node.condition)
        
        # Check if condition is a constant
        if isinstance(condition, IntegerLiteral):
            self.optimizations_applied += 1
            if condition.value != 0:  # True condition
                return self.eliminate_dead_code(node.then_statement)
            else:  # False condition
                if node.else_statement:
                    return self.eliminate_dead_code(node.else_statement)
                else:
                    # Return empty statement or null
                    return CompoundStatement([])
        
        # Process branches
        then_stmt = self.eliminate_dead_code(node.then_statement)
        else_stmt = None
        if node.else_statement:
            else_stmt = self.eliminate_dead_code(node.else_statement)
        
        return IfStatement(condition, then_stmt, else_stmt)

class LoopOptimizationPass(OptimizationPass):
    """
    Loop Optimization Pass
    
    Optimizes loop constructs:
    - Eliminate loops with constant false conditions
    - Optimize simple counting loops
    """
    
    def __init__(self):
        super().__init__("Loop Optimization")
    
    def optimize(self, node: ASTNode) -> ASTNode:
        """Apply loop optimizations to AST."""
        if isinstance(node, Program):
            optimized_declarations = []
            for declaration in node.declarations:
                optimized_declarations.append(self.optimize_loops(declaration))
            return Program(optimized_declarations)
        else:
            return self.optimize_loops(node)
    
    def optimize_loops(self, node: ASTNode) -> ASTNode:
        """Recursively optimize loops."""
        if isinstance(node, WhileStatement):
            return self.optimize_while_loop(node)
        elif isinstance(node, ForStatement):
            return self.optimize_for_loop(node)
        elif isinstance(node, CompoundStatement):
            node.statements = [self.optimize_loops(stmt) for stmt in node.statements]
        elif isinstance(node, IfStatement):
            node.then_statement = self.optimize_loops(node.then_statement)
            if node.else_statement:
                node.else_statement = self.optimize_loops(node.else_statement)
        elif isinstance(node, FunctionDeclaration):
            if node.body:
                node.body = self.optimize_loops(node.body)
        
        return node
    
    def optimize_while_loop(self, node: WhileStatement) -> ASTNode:
        """Optimize while loops."""
        # Check for constant false condition
        if isinstance(node.condition, IntegerLiteral) and node.condition.value == 0:
            self.optimizations_applied += 1
            return CompoundStatement([])  # Remove the loop entirely
        
        # Recursively optimize loop body
        node.body = self.optimize_loops(node.body)
        return node
    
    def optimize_for_loop(self, node: ForStatement) -> ASTNode:
        """Optimize for loops."""
        # Check for constant false condition
        if isinstance(node.condition, IntegerLiteral) and node.condition.value == 0:
            self.optimizations_applied += 1
            return CompoundStatement([])  # Remove the loop entirely
        
        # Recursively optimize loop body
        node.body = self.optimize_loops(node.body)
        return node

class PeepholeOptimizerPass(OptimizationPass):
    """
    Peephole Optimization Pass
    
    Performs assembly-level optimizations on generated code:
    - Remove redundant move instructions
    - Combine adjacent operations
    - Optimize register usage patterns
    """
    
    def __init__(self):
        super().__init__("Peephole Optimization")
        self.assembly_lines = []
    
    def optimize_assembly(self, assembly_code: str) -> str:
        """Apply peephole optimizations to assembly code."""
        lines = assembly_code.split('\n')
        self.assembly_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and labels
            if not line or line.endswith(':') or line.startswith('.'):
                self.assembly_lines.append(lines[i])
                i += 1
                continue
            
            # Look for optimization patterns
            optimized = False
            
            # Pattern 1: Remove redundant moves (movq %rax, %rax)
            if self.is_redundant_move(line):
                self.optimizations_applied += 1
                optimized = True
            
            # Pattern 2: Combine move and operation
            elif i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                combined = self.combine_move_operation(line, next_line)
                if combined:
                    self.assembly_lines.append(combined)
                    self.optimizations_applied += 1
                    i += 2  # Skip both lines
                    optimized = True
            
            # Pattern 3: Remove unnecessary zero operations
            elif self.is_zero_operation(line):
                self.optimizations_applied += 1
                optimized = True
            
            if not optimized:
                self.assembly_lines.append(lines[i])
            
            i += 1
        
        return '\n'.join(self.assembly_lines)
    
    def is_redundant_move(self, line: str) -> bool:
        """Check if line is a redundant move instruction."""
        if 'movq' in line:
            parts = line.split()
            if len(parts) >= 3:
                src = parts[1].rstrip(',')
                dst = parts[2].split('#')[0].strip()
                return src == dst
        return False
    
    def combine_move_operation(self, line1: str, line2: str) -> Optional[str]:
        """Try to combine move and arithmetic operation."""
        # Pattern: movq $const, %reg followed by addq %reg, %other
        if 'movq $' in line1 and 'addq' in line2:
            # Extract constant from first line
            parts1 = line1.split()
            if len(parts1) >= 3:
                const = parts1[1].rstrip(',')
                reg = parts1[2].split('#')[0].strip()
                
                # Check if second line uses this register
                parts2 = line2.split()
                if len(parts2) >= 3 and parts2[1].rstrip(',') == reg:
                    target = parts2[2].split('#')[0].strip()
                    # Combine into: addq $const, target
                    return f"    addq {const}, {target}                # combined add immediate"
        
        return None
    
    def is_zero_operation(self, line: str) -> bool:
        """Check for operations that have no effect."""
        # addq $0, %reg or subq $0, %reg
        return ('addq $0,' in line.replace(' ', '') or 
                'subq $0,' in line.replace(' ', '') or
                'imulq $1,' in line.replace(' ', ''))

class OptimizationManager:
    """
    Manages and orchestrates multiple optimization passes.
    
    Applies optimizations in the correct order:
    1. Constant Folding (enables other optimizations)
    2. Dead Code Elimination (removes unnecessary code)
    3. Loop Optimization (optimizes control flow)
    4. Peephole Optimization (assembly-level optimizations)
    """
    
    def __init__(self):
        self.passes = [
            ConstantFoldingPass(),
            DeadCodeEliminationPass(),
            LoopOptimizationPass(),
            PeepholeOptimizerPass()
        ]
        self.total_optimizations = 0
    
    def optimize_ast(self, ast: Program) -> Program:
        """Apply AST-level optimizations."""
        print("🔧 Applying AST-level optimizations...")
        
        optimized_ast = ast
        
        # Apply multiple passes until no more optimizations
        for pass_num in range(3):  # Maximum 3 iterations
            initial_count = sum(p.optimizations_applied for p in self.passes[:3])
            
            for opt_pass in self.passes[:3]:  # Skip peephole pass for AST
                optimized_ast = opt_pass.optimize(optimized_ast)
            
            final_count = sum(p.optimizations_applied for p in self.passes[:3])
            
            if final_count == initial_count:
                break  # No more optimizations possible
        
        # Report results
        for opt_pass in self.passes[:3]:
            opt_pass.report()
        
        self.total_optimizations = sum(p.optimizations_applied for p in self.passes[:3])
        print(f"   Total AST optimizations: {self.total_optimizations}")
        
        return optimized_ast
    
    def optimize_assembly(self, assembly_code: str) -> str:
        """Apply assembly-level optimizations."""
        print("🔧 Applying assembly-level optimizations...")
        
        # Apply peephole optimizations
        peephole_pass = self.passes[3]  # PeepholeOptimizerPass
        optimized_assembly = peephole_pass.optimize_assembly(assembly_code)
        
        peephole_pass.report()
        assembly_optimizations = peephole_pass.optimizations_applied
        
        print(f"   Total assembly optimizations: {assembly_optimizations}")
        print(f"   Overall optimizations applied: {self.total_optimizations + assembly_optimizations}")
        
        return optimized_assembly

# ============================================================================
# ADVANCED REGISTER ALLOCATION
# ============================================================================

class LiveInterval:
    """Represents the live range of a variable."""
    def __init__(self, variable: str, start: int, end: int):
        self.variable = variable
        self.start = start      # First use
        self.end = end          # Last use
        self.register = None    # Assigned register
        self.spilled = False    # Whether variable is spilled to memory
        self.spill_location = None  # Stack offset if spilled
    
    def __str__(self):
        return f"{self.variable}[{self.start}-{self.end}] → {self.register}"
    
    def overlaps(self, other: 'LiveInterval') -> bool:
        """Check if this interval overlaps with another."""
        return not (self.end < other.start or other.end < self.start)

class LiveVariableAnalysis:
    """
    Performs live variable analysis to determine variable lifetimes.
    
    Uses backward dataflow analysis to compute:
    - def[n]: Variables defined (written) at instruction n
    - use[n]: Variables used (read) at instruction n  
    - live_in[n]: Variables live at entry to instruction n
    - live_out[n]: Variables live at exit from instruction n
    """
    
    def __init__(self):
        self.instructions = []      # List of instruction objects
        self.def_sets = {}          # def[n] - variables defined at n
        self.use_sets = {}          # use[n] - variables used at n
        self.live_in = {}           # live_in[n] - variables live at entry
        self.live_out = {}          # live_out[n] - variables live at exit
        self.successors = {}        # Control flow successors
        self.variable_intervals = {} # Live intervals for each variable
    
    def analyze_function(self, function_ast: FunctionDeclaration) -> Dict[str, LiveInterval]:
        """Analyze live variables for a function and compute intervals."""
        print(f"   🔍 Analyzing live variables for: {function_ast.name}")
        
        # Step 1: Extract instructions and build CFG
        self.extract_instructions(function_ast.body)
        
        # Step 2: Compute def/use sets for each instruction
        self.compute_def_use_sets()
        
        # Step 3: Perform backward dataflow analysis
        self.compute_liveness()
        
        # Step 4: Compute live intervals
        self.compute_live_intervals()
        
        print(f"      Found {len(self.variable_intervals)} variables with live intervals")
        for var, interval in self.variable_intervals.items():
            print(f"      {interval}")
        
        return self.variable_intervals
    
    def extract_instructions(self, node: ASTNode, instruction_id: int = 0):
        """Extract linear instruction sequence from AST."""
        self.instructions = []
        self._extract_recursive(node, 0)
    
    def _extract_recursive(self, node: ASTNode, inst_id: int) -> int:
        """Recursively extract instructions from AST nodes."""
        if isinstance(node, CompoundStatement):
            for stmt in node.statements:
                inst_id = self._extract_recursive(stmt, inst_id)
        
        elif isinstance(node, VariableDeclaration):
            # Variable definition
            self.instructions.append(('def', inst_id, node.name, node.initializer))
            inst_id += 1
        
        elif isinstance(node, AssignmentExpression):
            # Assignment: use RHS, then def LHS
            if isinstance(node.left, Identifier):
                self.instructions.append(('assign', inst_id, node.left.name, node.right))
                inst_id += 1
        
        elif isinstance(node, BinaryExpression):
            # Binary operation: use both operands
            self.instructions.append(('binop', inst_id, node.operator, node.left, node.right))
            inst_id += 1
        
        elif isinstance(node, CallExpression):
            # Function call: use all arguments
            if isinstance(node.function, Identifier):
                self.instructions.append(('call', inst_id, node.function.name, node.arguments))
                inst_id += 1
        
        elif isinstance(node, ReturnStatement):
            # Return: use return value
            self.instructions.append(('return', inst_id, node.expression))
            inst_id += 1
        
        elif isinstance(node, IfStatement):
            # Conditional: use condition, then branches
            self.instructions.append(('cond', inst_id, node.condition))
            cond_id = inst_id
            inst_id += 1
            
            then_start = inst_id
            inst_id = self._extract_recursive(node.then_statement, inst_id)
            then_end = inst_id - 1
            
            if node.else_statement:
                else_start = inst_id
                inst_id = self._extract_recursive(node.else_statement, inst_id)
                else_end = inst_id - 1
                # Set up control flow
                self.successors[cond_id] = [then_start, else_start]
            else:
                self.successors[cond_id] = [then_start, inst_id]
        
        elif isinstance(node, ExpressionStatement):
            if node.expression:
                inst_id = self._extract_recursive(node.expression, inst_id)
        
        return inst_id
    
    def compute_def_use_sets(self):
        """Compute def and use sets for each instruction."""
        for i, instruction in enumerate(self.instructions):
            self.def_sets[i] = set()
            self.use_sets[i] = set()
            
            inst_type = instruction[0]
            
            if inst_type == 'def':
                # Variable definition: def = {var}, use = variables in initializer
                var_name = instruction[2]
                initializer = instruction[3]
                self.def_sets[i].add(var_name)
                if initializer:
                    self.use_sets[i].update(self._get_variables_used(initializer))
            
            elif inst_type == 'assign':
                # Assignment: def = {lhs}, use = variables in rhs
                lhs_var = instruction[2]
                rhs_expr = instruction[3]
                self.def_sets[i].add(lhs_var)
                self.use_sets[i].update(self._get_variables_used(rhs_expr))
            
            elif inst_type == 'binop':
                # Binary operation: use = variables in both operands
                left_expr = instruction[3]
                right_expr = instruction[4]
                self.use_sets[i].update(self._get_variables_used(left_expr))
                self.use_sets[i].update(self._get_variables_used(right_expr))
            
            elif inst_type == 'call':
                # Function call: use = variables in arguments
                arguments = instruction[3]
                for arg in arguments:
                    self.use_sets[i].update(self._get_variables_used(arg))
            
            elif inst_type == 'return':
                # Return: use = variables in return expression
                return_expr = instruction[2]
                if return_expr:
                    self.use_sets[i].update(self._get_variables_used(return_expr))
            
            elif inst_type == 'cond':
                # Condition: use = variables in condition
                condition = instruction[2]
                self.use_sets[i].update(self._get_variables_used(condition))
    
    def _get_variables_used(self, expr: ASTNode) -> Set[str]:
        """Extract all variable names used in an expression."""
        variables = set()
        
        if isinstance(expr, Identifier):
            variables.add(expr.name)
        elif isinstance(expr, BinaryExpression):
            variables.update(self._get_variables_used(expr.left))
            variables.update(self._get_variables_used(expr.right))
        elif isinstance(expr, UnaryExpression):
            variables.update(self._get_variables_used(expr.operand))
        elif isinstance(expr, CallExpression):
            for arg in expr.arguments:
                variables.update(self._get_variables_used(arg))
        elif isinstance(expr, AssignmentExpression):
            variables.update(self._get_variables_used(expr.left))
            variables.update(self._get_variables_used(expr.right))
        
        return variables
    
    def compute_liveness(self):
        """Compute live_in and live_out sets using backward dataflow analysis."""
        # Initialize all sets to empty
        num_instructions = len(self.instructions)
        for i in range(num_instructions):
            self.live_in[i] = set()
            self.live_out[i] = set()
        
        # Iteratively compute liveness until convergence
        changed = True
        iterations = 0
        
        while changed and iterations < 50:  # Prevent infinite loops
            changed = False
            iterations += 1
            
            # Process instructions in reverse order (backward analysis)
            for i in range(num_instructions - 1, -1, -1):
                old_live_in = self.live_in[i].copy()
                old_live_out = self.live_out[i].copy()
                
                # live_out[i] = Union of live_in of all successors
                if i in self.successors:
                    for succ in self.successors[i]:
                        if succ < num_instructions:
                            self.live_out[i].update(self.live_in[succ])
                elif i + 1 < num_instructions:
                    # Default: next instruction is successor
                    self.live_out[i].update(self.live_in[i + 1])
                
                # live_in[i] = use[i] ∪ (live_out[i] - def[i])
                self.live_in[i] = self.use_sets[i].union(
                    self.live_out[i] - self.def_sets[i]
                )
                
                # Check if anything changed
                if (old_live_in != self.live_in[i] or 
                    old_live_out != self.live_out[i]):
                    changed = True
        
        print(f"      Liveness analysis converged in {iterations} iterations")
    
    def compute_live_intervals(self):
        """Compute live intervals for each variable."""
        # Find first and last occurrence of each variable
        first_use = {}
        last_use = {}
        
        for i in range(len(self.instructions)):
            # Variables in live_in are live at this point
            for var in self.live_in[i]:
                if var not in first_use:
                    first_use[var] = i
                last_use[var] = i
            
            # Variables in live_out are live after this point
            for var in self.live_out[i]:
                if var not in first_use:
                    first_use[var] = i
                last_use[var] = i
        
        # Create live intervals
        self.variable_intervals = {}
        for var in first_use:
            start = first_use[var]
            end = last_use.get(var, start)
            self.variable_intervals[var] = LiveInterval(var, start, end)

class AdvancedRegisterAllocator:
    """
    Advanced Register Allocator using Linear Scan Algorithm.
    
    Performs sophisticated register allocation with:
    - Live variable analysis
    - Register spilling when needed
    - Efficient register reuse
    - Calling convention awareness
    """
    
    def __init__(self):
        # Available registers (exclude special purpose ones)
        self.general_registers = [
            'rbx', 'r12', 'r13', 'r14', 'r15',  # Callee-saved (preferred)
            'r10', 'r11',                        # Caller-saved scratch
            'r8', 'r9'                          # Parameter registers (reusable)
        ]
        
        # Parameter registers (System V AMD64 calling convention)
        self.param_registers = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        
        # Special registers
        self.return_register = 'rax'
        self.stack_pointer = 'rsp'
        self.base_pointer = 'rbp'
        
        # Allocation state
        self.active_intervals = []      # Currently active live intervals
        self.register_assignments = {}  # Variable -> register mapping
        self.spilled_variables = {}     # Variable -> stack offset mapping
        self.stack_offset = 0          # Current stack offset for spills
        
        # Statistics
        self.total_variables = 0
        self.registers_used = 0
        self.variables_spilled = 0
    
    def allocate_registers(self, function_ast: FunctionDeclaration) -> Dict[str, str]:
        """
        Perform register allocation for a function using linear scan algorithm.
        
        Returns mapping from variable names to register names or stack locations.
        """
        print(f"   🎯 Performing register allocation for: {function_ast.name}")
        
        # Step 1: Perform live variable analysis
        liveness_analyzer = LiveVariableAnalysis()
        live_intervals = liveness_analyzer.analyze_function(function_ast)
        
        if not live_intervals:
            print("      No variables to allocate")
            return {}
        
        # Step 2: Sort intervals by start point (linear scan requirement)
        sorted_intervals = sorted(live_intervals.values(), key=lambda x: x.start)
        
        # Step 3: Allocate parameters to their conventional registers
        self._allocate_parameters(function_ast.parameters)
        
        # Step 4: Linear scan register allocation
        self._linear_scan_allocation(sorted_intervals)
        
        # Step 5: Generate final allocation mapping
        allocation_map = self._generate_allocation_map()
        
        # Report statistics
        self.total_variables = len(live_intervals)
        self.registers_used = len(set(allocation_map.values()) - {'spilled'})
        self.variables_spilled = sum(1 for v in allocation_map.values() if v == 'spilled')
        
        print(f"      ✅ Allocated {self.total_variables} variables:")
        print(f"         📊 {self.registers_used} in registers, {self.variables_spilled} spilled")
        
        for var, location in allocation_map.items():
            if location != 'spilled':
                print(f"         {var} → %{location}")
            else:
                offset = self.spilled_variables[var]
                print(f"         {var} → {offset}(%rbp) [spilled]")
        
        return allocation_map
    
    def _allocate_parameters(self, parameters: List):
        """Allocate function parameters to calling convention registers."""
        for i, param in enumerate(parameters):
            if i < len(self.param_registers):
                reg = self.param_registers[i]
                self.register_assignments[param.name] = reg
                print(f"         Parameter {param.name} → %{reg}")
    
    def _linear_scan_allocation(self, intervals: List[LiveInterval]):
        """
        Linear scan register allocation algorithm.
        
        For each interval in sorted order:
        1. Expire old intervals that no longer overlap
        2. If free register available, assign it
        3. Otherwise, spill least recently used interval
        """
        for interval in intervals:
            # Skip if already allocated (e.g., function parameters)
            if interval.variable in self.register_assignments:
                continue
            
            # Step 1: Expire old intervals
            self._expire_old_intervals(interval)
            
            # Step 2: Try to allocate a register
            if len(self.active_intervals) < len(self.general_registers):
                # Free register available
                reg = self._get_free_register()
                interval.register = reg
                self.register_assignments[interval.variable] = reg
                self.active_intervals.append(interval)
                self.active_intervals.sort(key=lambda x: x.end)  # Keep sorted by end time
            else:
                # No free register - need to spill
                self._spill_at_interval(interval)
    
    def _expire_old_intervals(self, current_interval: LiveInterval):
        """Remove intervals that no longer overlap with current interval."""
        expired = []
        for active in self.active_intervals:
            if active.end < current_interval.start:
                # This interval has expired - free its register
                expired.append(active)
        
        for exp in expired:
            self.active_intervals.remove(exp)
    
    def _get_free_register(self) -> str:
        """Find a free general-purpose register."""
        used_registers = {interval.register for interval in self.active_intervals 
                         if interval.register}
        
        for reg in self.general_registers:
            if reg not in used_registers and reg not in self.register_assignments.values():
                return reg
        
        # Fallback - should not happen if logic is correct
        return self.general_registers[0]
    
    def _spill_at_interval(self, interval: LiveInterval):
        """
        Spill strategy: spill the interval that ends last.
        
        If current interval ends before the last active interval,
        spill the last active interval and allocate its register to current.
        Otherwise, spill the current interval.
        """
        # Find interval that ends last
        last_interval = max(self.active_intervals, key=lambda x: x.end)
        
        if interval.end < last_interval.end:
            # Spill the last interval and use its register
            interval.register = last_interval.register
            self.register_assignments[interval.variable] = last_interval.register
            
            # Spill the last interval
            self._spill_variable(last_interval)
            
            # Remove last interval and add current
            self.active_intervals.remove(last_interval)
            self.active_intervals.append(interval)
            self.active_intervals.sort(key=lambda x: x.end)
        else:
            # Spill current interval
            self._spill_variable(interval)
    
    def _spill_variable(self, interval: LiveInterval):
        """Spill a variable to memory (stack)."""
        self.stack_offset += 8  # 8 bytes for 64-bit values
        interval.spilled = True
        interval.spill_location = self.stack_offset
        self.spilled_variables[interval.variable] = self.stack_offset
        
        # Remove from register assignment if present
        if interval.variable in self.register_assignments:
            del self.register_assignments[interval.variable]
    
    def _generate_allocation_map(self) -> Dict[str, str]:
        """Generate final allocation mapping."""
        allocation_map = {}
        
        # Add register assignments
        for var, reg in self.register_assignments.items():
            allocation_map[var] = reg
        
        # Add spilled variables
        for var in self.spilled_variables:
            allocation_map[var] = 'spilled'
        
        return allocation_map

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
        self.code_generator = CodeGenerator()
        self.optimizer = OptimizationManager()
        self.optimization_level = 1  # Default optimization level
    
    def set_optimization_level(self, level: int):
        """Set optimization level (0=none, 1=basic, 2=aggressive)."""
        self.optimization_level = level
    
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
            
            # Phase 3.5: AST Optimization  
            if self.optimization_level > 0:
                print("🔧 Phase 3.5: AST Optimization...")
                optimized_ast = self.optimizer.optimize_ast(ast)
                print("   ✅ AST optimization completed successfully!")
            else:
                print("⏩ Phase 3.5: AST Optimization - SKIPPED (O0)")
                optimized_ast = ast
            
            # Phase 4: Code Generation
            print("⚙️ Phase 4: Code Generation...")
            assembly_code = self.code_generator.generate(optimized_ast)
            
            # Phase 4.5: Assembly Optimization
            if self.optimization_level > 0:
                print("🔧 Phase 4.5: Assembly Optimization...")
                optimized_assembly = self.optimizer.optimize_assembly(assembly_code)
                print("   ✅ Assembly optimization completed successfully!")
            else:
                print("⏩ Phase 4.5: Assembly Optimization - SKIPPED (O0)")
                optimized_assembly = assembly_code
            
            # Write optimized assembly to output file
            output_filename = source_file.replace('.c', '.s')
            with open(output_filename, 'w') as f:
                f.write(optimized_assembly)
            
            print(f"   ✅ Generated optimized assembly: {output_filename}")
            print(f"   Generated {len(optimized_assembly.split())} lines of x86-64 assembly")
            
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
    
    def compile_to_executable(self, source_file: str, output_file: str = None) -> bool:
        """Compile C source to executable binary."""
        try:
            # First compile to assembly
            if not self.compile(source_file):
                return False
            
            # Determine file names
            assembly_file = source_file.replace('.c', '.s')
            if not output_file:
                output_file = source_file.replace('.c', '')
            
            # Phase 5: Assembly & Linking
            print("🔗 Phase 5: Assembly & Linking...")
            
            # Use GNU assembler and linker
            import subprocess
            
            # Assemble to object file
            object_file = source_file.replace('.c', '.o')
            assemble_cmd = ['as', '--64', '-o', object_file, assembly_file]
            
            result = subprocess.run(assemble_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Assembly failed: {result.stderr}")
                return False
            
            print(f"   ✅ Assembled object file: {object_file}")
            
            # Link to executable
            link_cmd = ['ld', '-o', output_file, object_file]
            
            result = subprocess.run(link_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Linking failed: {result.stderr}")
                return False
            
            print(f"   ✅ Created executable: {output_file}")
            print(f"   Run with: ./{output_file}")
            
            return True
            
        except FileNotFoundError as e:
            print(f"❌ Tool not found: {e}. Install GNU binutils (as, ld)")
            return False
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point for the C compiler."""
    import argparse
    
    parser = argparse.ArgumentParser(description='🔧 VIBE-PY C Compiler')
    parser.add_argument('source', help='C source file (.c)')
    parser.add_argument('-o', '--output', help='Output file name')
    parser.add_argument('-S', '--assembly', action='store_true', 
                       help='Generate assembly only (.s file)')
    parser.add_argument('-c', '--compile-only', action='store_true',
                       help='Compile to object file only (.o)')
    parser.add_argument('--executable', action='store_true',
                       help='Compile to executable binary (requires GNU binutils)')
    parser.add_argument('-O0', '--no-optimize', action='store_true',
                       help='Disable all optimizations')
    parser.add_argument('-O1', '--optimize', action='store_true',
                       help='Enable basic optimizations (default)')
    parser.add_argument('-O2', '--optimize-more', action='store_true',
                       help='Enable aggressive optimizations')
    parser.add_argument('--no-advanced-regs', action='store_true',
                       help='Disable advanced register allocation (use simple stack allocation)')
    
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n📖 Examples:")
        print("  python3 c-compiler.py program.c                    # Generate assembly")
        print("  python3 c-compiler.py program.c -S                 # Generate assembly only")
        print("  python3 c-compiler.py program.c --executable       # Create executable")
        print("  python3 c-compiler.py program.c -o my_program      # Specify output name")
        sys.exit(1)
    
    args = parser.parse_args()
    
    if not args.source.endswith('.c'):
        print("❌ Error: Source file must have .c extension")
        sys.exit(1)
    
    compiler = CCompiler()
    
    # Set optimization level
    if args.no_optimize:
        compiler.set_optimization_level(0)
    elif args.optimize_more:
        compiler.set_optimization_level(2)
    elif args.optimize:
        compiler.set_optimization_level(1)
    # Default is already 1
    
    # Configure register allocation
    if args.no_advanced_regs:
        compiler.code_generator.set_advanced_allocation(False)
    
    if args.executable:
        # Compile to executable
        success = compiler.compile_to_executable(args.source, args.output)
    else:
        # Default: compile to assembly
        success = compiler.compile(args.source, args.output)
    
    if not success:
        sys.exit(1)
    
    print("🎉 Compilation completed successfully!")

if __name__ == "__main__":
    main()