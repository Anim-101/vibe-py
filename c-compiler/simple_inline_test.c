// Simple function inlining test
int add(int a, int b) {
    return a + b;
}

int main() {
    int x = add(3, 5);  // Should find this call
    int y = add(x, 2);  // Should find this call too
    return x + y;
}