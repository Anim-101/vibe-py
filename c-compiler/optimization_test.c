// optimization_test.c - Test program to showcase compiler optimizations

int compute_value() {
    // These should be constant-folded
    int result = 2 + 3 * 4;     // Should become: int result = 14;
    result = result + 0;        // Should become: result = result; (then eliminated)
    result = result * 1;        // Should become: result = result; (then eliminated)
    
    // Dead code after return
    if (1) {
        return result;
        int unreachable = 42;   // Should be eliminated
    } else {
        return 0;               // Should be eliminated (condition is always true)
    }
    
    return -1;                  // Should be eliminated (unreachable)
}

int test_loops() {
    int sum = 0;
    int i = 0;
    
    // Loop with constant condition
    while (0) {                 // Should be eliminated entirely
        sum = sum + 1;
        i = i + 1;
    }
    
    // Normal loop that should remain
    while (i < 5) {
        sum = sum + i;
        i = i + 1;
    }
    
    return sum;
}

int main() {
    int x = 10 + 5;            // Should be constant-folded to: int x = 15;
    int y = x * 0;             // Should become: int y = 0;
    int z = 0 + x;             // Should become: int z = x;
    
    // Function calls should remain
    int result1 = compute_value();
    int result2 = test_loops();
    
    // Dead branch elimination
    if (0) {                   // Should eliminate entire if block
        return 999;
    }
    
    return result1 + result2;
}