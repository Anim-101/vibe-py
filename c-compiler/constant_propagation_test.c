// Enhanced Constant Propagation Test
// Tests advanced constant folding and algebraic simplifications

// Function returning a constant - should be propagated
int get_constant() {
    return 42;
}

// Function with complex constant expressions
int constant_expressions() {
    // Basic arithmetic that should be folded
    int a = 2 + 3;           // → 5
    int b = 10 * 4;          // → 40
    int c = 15 / 3;          // → 5
    int d = 20 - 8;          // → 12
    
    // Algebraic simplifications
    int e = a + 0;           // → a (which is 5)
    int f = b * 1;           // → b (which is 40)
    int g = c - 0;           // → c (which is 5)
    int h = d / 1;           // → d (which is 12)
    
    // Zero optimizations
    int i = 0 * 999;         // → 0
    int j = 0 + e;           // → e (which is 5)
    
    return a + b + c + d + e + f + g + h + i + j;
}

// Function with conditional constant propagation
int conditional_constants(int x) {
    // Always true condition - else branch should be eliminated
    if (1) {
        x = x + 10;
    } else {
        x = x - 100;         // Unreachable
    }
    
    // Always false condition - then branch should be eliminated  
    if (0) {
        x = x * 999;         // Unreachable
    }
    
    // Constant comparison
    if (5 > 3) {             // Always true
        x = x + 1;
    } else {
        x = x - 1;           // Unreachable
    }
    
    return x;
}

// Function with power-of-2 optimizations
int power_optimizations() {
    int x = 10;
    
    // Power of 2 multiplications (could be optimized to shifts)
    int a = x * 2;           // x << 1
    int b = x * 4;           // x << 2  
    int c = x * 8;           // x << 3
    int d = x * 16;          // x << 4
    
    return a + b + c + d;
}

// Function with constant variables that should be propagated
int variable_propagation() {
    int const_var = 100;     // This should be propagated
    int result = const_var + 50;  // Should become 100 + 50 = 150
    
    const_var = 200;         // Update constant  
    result = result + const_var;   // Should become result + 200
    
    return result;
}

int main() {
    // Call to constant function - should be replaced with 42
    int a = get_constant();
    
    // Complex constant expressions
    int b = constant_expressions();
    
    // Conditional constants
    int c = conditional_constants(5);
    
    // Power optimizations
    int d = power_optimizations();
    
    // Variable propagation
    int e = variable_propagation();
    
    // Should result in highly optimized code
    return a + b + c + d + e;
}