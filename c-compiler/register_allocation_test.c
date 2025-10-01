// register_allocation_test.c - Test program for advanced register allocation

int calculate_complex(int a, int b, int c, int d) {
    // Many local variables to test register allocation
    int x = a + b;          // Should get register
    int y = c * d;          // Should get register  
    int z = x - y;          // Should get register
    int w = x + y + z;      // May need spilling
    int v = w * 2;          // May be spilled
    int u = v + a - b;      // Complex expression
    
    // Test variable reuse and lifetime
    if (u > 100) {
        int temp = u / 2;   // Short lifetime variable
        return temp + x;
    }
    
    return u + z;
}

int test_register_pressure() {
    // High register pressure scenario
    int a = 1;
    int b = 2; 
    int c = 3;
    int d = 4;
    int e = 5;
    int f = 6;
    int g = 7;
    int h = 8;
    int i = 9;
    int j = 10;
    
    // Use all variables to force register allocation decisions
    int result = a + b + c + d + e + f + g + h + i + j;
    
    // Reuse some variables (their registers can be freed)
    a = result * 2;
    b = a + result;
    
    return b;
}

int main() {
    // Test function calls with register allocation
    int result1 = calculate_complex(10, 20, 30, 40);
    int result2 = test_register_pressure();
    
    // Local computation
    int final = result1 + result2;
    
    return final;
}