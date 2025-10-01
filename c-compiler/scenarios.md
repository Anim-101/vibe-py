# Scenario 1

- Make simple compilation using python

# Scemario 2

- Full compilation pipeline design: Lexer → Parser → AST → Semantic Analysis → Code Generation
- Professional modular structure with clear separation of concerns
- Comprehensive token definitions for all C language elements
- 67 different token types including all C keywords, operators, and punctuation
- Complete C keyword recognition (int, float, if, while, return, etc.)
- Multi-character operator support (++, --, <=, >=, &&, ||, etc.)
- String and character literal parsing with escape sequence handling
- Comment handling (both // and /* */ styles)
- Numeric parsing for integers and floats
- Error handling with line/column location tracking
- Complete AST node hierarchy for all C constructs
- Function declarations, variable declarations, statements, expressions
- Control flow structures (if, while, for)
- Binary/unary expressions, function calls, literals