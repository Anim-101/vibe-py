// Comprehensive test for C compiler parser
int global_var = 100;

int factorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

float calculate_average(int a, int b, int c) {
    int sum = a + b + c;
    float average = sum / 3.0;
    return average;
}

int main() {
    int x = 5;
    int y = 10;
    int result;
    
    // Test arithmetic
    result = x + y * 2 - 3;
    
    // Test comparison and logical operators  
    if (x > 0 && y < 20) {
        result = result + 1;
    }
    
    // Test function calls
    int fact5 = factorial(5);
    float avg = calculate_average(x, y, result);
    
    // Test loops
    int i = 0;
    while (i < 10) {
        i = i + 1;
    }
    
    for (int j = 0; j < 5; j = j + 1) {
        result = result * 2;
    }
    
    return result;
}