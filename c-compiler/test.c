#include <stdio.h>

int main() {
    int x = 42;
    int y = 10;
    int sum = x + y;
    
    printf("Hello, World!\n");
    printf("Sum: %d\n", sum);
    
    if (sum > 50) {
        printf("Sum is greater than 50\n");
    } else {
        printf("Sum is 50 or less\n");
    }
    
    return 0;
}