// loop_unrolling_test.c - Comprehensive test for loop unrolling optimization

int test_small_loop() {
    // Small loop - should be FULLY unrolled
    int sum = 0;
    for (int i = 0; i < 4; i++) {
        sum = sum + i * 2;
    }
    return sum;
}

int test_medium_loop() {
    // Medium loop - should be PARTIALLY unrolled
    int result = 1;
    for (int i = 1; i <= 8; i++) {
        result = result * i;
    }
    return result;
}

int test_array_sum() {
    // Array processing loop - great candidate for unrolling
    int numbers[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    int total = 0;
    
    for (int i = 0; i < 10; i++) {
        total = total + numbers[i];
    }
    
    return total;
}

int test_nested_loops() {
    // Nested loops - should unroll inner loop
    int sum = 0;
    
    for (int i = 0; i < 3; i++) {
        // Inner loop should be unrolled
        for (int j = 0; j < 4; j++) {
            sum = sum + i + j;
        }
    }
    
    return sum;
}

int test_complex_body() {
    // Loop with complex body - should NOT be unrolled
    int result = 0;
    
    for (int i = 0; i < 100; i++) {
        if (i > 50) {
            result = result + i * i;
        } else {
            result = result - i;
        }
        
        // Complex computation
        int temp = i * 3 + 7;
        result = result + temp / 2;
    }
    
    return result;
}

int main() {
    int result1 = test_small_loop();      // Full unrolling expected
    int result2 = test_medium_loop();     // Partial unrolling expected  
    int result3 = test_array_sum();       // Partial unrolling expected
    int result4 = test_nested_loops();    // Inner loop unrolling expected
    int result5 = test_complex_body();    // No unrolling expected
    
    return result1 + result2 + result3 + result4 + result5;
}