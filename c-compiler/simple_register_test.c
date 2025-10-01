// simple_register_test.c - Simple test for register allocation comparison

int compute(int a, int b) {
    int x = a + b;
    int y = x * 2;
    int z = y - a;
    return z;
}

int main() {
    int result = compute(10, 20);
    return result;
}