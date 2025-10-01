// simple_semantic_test.c - Simplified test for semantic analysis

int global_var = 42;

int add(int a, int b) {
    int result = a + b;
    return result;
}

float multiply(float x, float y) {
    return x * y;
}

void print_hello() {
    return;
}

int main() {
    int x = 10;
    int y = 20;
    float f = 3.14;
    
    int sum = add(x, y);
    float product = multiply(f, 2.5);
    
    print_hello();
    
    if (x > y) {
        x = y;
    }
    
    return 0;
}