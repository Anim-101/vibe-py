// simple_opt_test.c - Simpler test for optimization verification

int main() {
    int x = 2 + 3;
    int y = x * 1;
    int z = y + 0;
    
    if (1) {
        return z;
    } else {
        return 0;
    }
}