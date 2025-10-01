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

# Scenario 3

- 4 top-level declarations parsed from complex C code
- Function declarations with parameters and bodies
- Variable declarations with initializers
- Global variables properly recognized
- Compound statements ({ ... } blocks)
- If/else statements with conditions
- While loops with proper condition parsing
- Variable declarations within function bodies
- Return statements with expressions
- Expression statements (assignments, function calls)
- Binary expressions: x + y * 2 - 3 (correctly handles precedence!)
- Comparison operators: x > 0 && y < 20
- Logical operators: &&, ||
- Assignment expressions: result = result + 1
- Function calls: factorial(5), calculate_sum(x, y, result)
- Parenthesized expressions: Proper grouping
- Error recovery: Continues parsing after syntax errors
- Synchronization: Finds statement boundaries for recovery
- Precise error location: Line and column numbers
- Descriptive messages: Clear error descriptions