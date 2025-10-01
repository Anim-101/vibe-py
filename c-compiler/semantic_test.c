// semantic_test.c - Comprehensive test for semantic analysis
// Tests type checking, symbol tables, scoping, and function validation

#include <stdio.h>

// Global variables
int global_counter = 0;
float pi = 3.14159;

// Function declarations
int add_numbers(int a, int b);
float calculate_area(float radius);
void print_message();

// Main function
int main() {
    // Local variable declarations with type checking
    int x = 10;
    int y = 20;
    float result = 0.0;
    
    // Function calls with argument type checking
    int sum = add_numbers(x, y);
    result = calculate_area(pi);
    
    // Arithmetic expressions with type compatibility
    int total = sum + global_counter;
    float final_result = result * 2.5;
    
    // Assignment type checking
    x = sum;           // int = int (OK)
    result = x;        // float = int (OK - type promotion)
    
    // Conditional statements
    if (x > y) {
        print_message();
    } else {
        printf("Numbers are equal or x is smaller\n");
    }
    
    // Loop with scoping
    for (int i = 0; i < 5; i++) {
        int local_var = i * 2;  // Local scope variable
        total += local_var;
    }
    
    // While loop
    int counter = 0;
    while (counter < 3) {
        counter++;
        global_counter = counter;
    }
    
    return 0;
}

// Function definitions
int add_numbers(int a, int b) {
    int result = a + b;
    return result;  // Type matches return type
}

float calculate_area(float radius) {
    float area = pi * radius * radius;
    return area;    // Type matches return type
}

void print_message() {
    printf("Hello from semantic analysis test!\n");
    // No return statement needed for void function
}