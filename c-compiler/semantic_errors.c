// semantic_errors.c - Test file with intentional semantic errors
// This file should trigger various semantic analysis errors

#include <stdio.h>

// Function with incorrect return type usage
int wrong_return() {
    return 3.14;  // ERROR: returning float from int function
}

// Main function with semantic errors
int main() {
    // Undefined variable usage
    int x = undefined_var;  // ERROR: undefined_var not declared
    
    // Type mismatch in assignment
    int number = "hello";   // ERROR: cannot assign string to int
    
    // Undeclared function call
    unknown_function(x);    // ERROR: unknown_function not declared
    
    // Variable redeclaration in same scope
    int y = 5;
    int y = 10;             // ERROR: y already declared in this scope
    
    // Wrong number of arguments to function
    printf();              // ERROR: printf expects at least 1 argument
    
    // Type incompatible operation
    int result = x + "text"; // ERROR: cannot add int and string
    
    // Assignment to incompatible type
    char c = 1000;          // WARNING/ERROR: value too large for char
    
    // Function call on non-function
    int func_var = 42;
    func_var(5);            // ERROR: func_var is not a function
    
    // Missing return in non-void function
    // This function should return int but no return statement at end
    
    return 0;
}

// Function with missing return
int missing_return_func() {
    int x = 10;
    // ERROR: no return statement in non-void function
}

// Void function trying to return value
void void_with_return() {
    return 42;              // ERROR: void function cannot return value
}