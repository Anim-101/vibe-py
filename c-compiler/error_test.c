int x = 5;

int add(int a, int b) {
    return a + b;
}

int main() {
    int result = add(x, y);     // ERROR: y is undefined
    int z = 10;
    int z = 20;                 // ERROR: z redeclared
    
    char c = add(1, 2);        // ERROR: cannot assign int to char (type mismatch)
    
    unknown_func();            // ERROR: undefined function
    
    return 0;
}