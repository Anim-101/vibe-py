// demo_optimizations.c - Showcase different optimization levels

int main() {
    int a = 5 + 10;
    int b = a * 1;
    int c = b + 0;
    int d = 0 + c;
    
    if (1) {
        return d;
        int never_reached = 999;
    }
    
    return -1;
}