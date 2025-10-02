// simple_unroll_test.c - Simple test for loop unrolling verification

int main() {
    // Perfect candidate for full unrolling: 3 iterations, simple body
    int sum = 0;
    for (int i = 0; i < 3; i++) {
        sum = sum + i;
    }
    
    return sum;  // Should return 0 + 1 + 2 = 3
}