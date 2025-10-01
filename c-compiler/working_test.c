int global_var = 100;

int factorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

int calculate_sum(int a, int b, int c) {
    int sum = a + b + c;
    return sum;
}

int main() {
    int x = 5;
    int y = 10;
    int result;
    
    result = x + y * 2 - 3;
    
    if (x > 0 && y < 20) {
        result = result + 1;
    }
    
    int fact5 = factorial(5);
    int sum_result = calculate_sum(x, y, result);
    
    int i = 0;
    while (i < 10) {
        i = i + 1;
    }
    
    return result;
}