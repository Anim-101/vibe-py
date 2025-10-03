// Enhanced Dead Code Elimination Test
// Tests various scenarios for advanced code removal

// Unused function - should be removed
int unused_function(int x) {
    return x * 2;
}

// Function with unreachable code
int function_with_unreachable_code(int a) {
    if (a > 0) {
        return a + 1;
        int unreachable = 42;  // Dead code after return
        a = unreachable;       // More dead code
    }
    return 0;
}

// Function with unused variables
int function_with_unused_vars(int x) {
    int unused_var = 10;      // Never read - should be removed
    int used_var = 20;        // Used below - should be kept
    int dead_store = 30;      // Written but never read - should be removed
    dead_store = 40;          // Dead store
    
    return used_var + x;
}

// Function with constant conditions
int function_with_constant_conditions(int x) {
    if (1) {                  // Always true - else branch should be removed
        x = x + 1;
    } else {
        x = x - 1;            // Unreachable - should be removed
    }
    
    if (0) {                  // Always false - then branch should be removed
        x = x * 2;            // Unreachable - should be removed
    }
    
    return x;
}

// Main function - should always be kept
int main() {
    // Call to used function
    int result = function_with_unreachable_code(5);
    
    // Call with unused variables
    result = function_with_unused_vars(result);
    
    // Call with constant conditions  
    result = function_with_constant_conditions(result);
    
    // Note: unused_function is never called, so should be removed
    
    return result;
}