// Function Inlining Test
// Tests various inlining scenarios and optimizations

// Small utility functions - good candidates for inlining
int add(int a, int b) {
    return a + b;
}

int multiply(int x, int y) {
    return x * y;
}

int square(int n) {
    return multiply(n, n);  // This calls another function
}

// Larger function - should NOT be inlined
int complex_calculation(int a, int b, int c) {
    int result = 0;
    if (a > 0) {
        result = add(a, b);
        if (b > 5) {
            result = multiply(result, c);
        } else {
            result = result + c;
        }
    } else {
        result = multiply(a, c);
    }
    return result;
}

int main() {
    int x = 10;
    int y = 5;
    
    // These function calls should be inlined
    int sum = add(x, y);           // Called multiple times - good candidate
    int prod = multiply(x, 3);     // Simple function, frequently used
    int sq = square(4);            // Small function calling another small function
    
    // More calls to same functions - increases inlining value
    int sum2 = add(sum, prod);     // Second call to add()
    int prod2 = multiply(sq, 2);   // Second call to multiply()
    
    // This should NOT be inlined due to complexity
    int complex = complex_calculation(x, y, sum);
    
    return sum + prod + sq + complex;
}