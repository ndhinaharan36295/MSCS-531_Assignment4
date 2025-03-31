#include <stdio.h>

// Function to test arithmetic operations
int arithmetic_ops(int a, int b) {
    int c = a + b;      // Execute stage (ALU)
    int d = c * a;      // Execute stage (ALU)
    int e = d - b;      // Execute stage (ALU)
    return e;
}

// Function to test memory accesses
void memory_ops(int* array, int size) {
    // Memory stage operations
    for (int i = 0; i < size; i++) {
        array[i] = i * 2;       // Store (memory stage)
    }

    for (int i = 0; i < size; i++) {
        array[i] += array[size-i-1];  // Load + ALU + Store (multiple stages)
    }
}

// Function with control flow
void control_flow(int x) {
    // Tests branch prediction
    if (x > 10) {           // Execute (comparison)
        printf("x is large\n");
    } else {
        printf("x is small\n");
    }

    // Loop with dependencies
    for (int i = 0; i < x; i++) {
        x += i % 2;          // ALU
    }
}

int main() {
    printf("Starting pipeline test...\n");

    // Test arithmetic operations
    int result = arithmetic_ops(5, 3);
    printf("Arithmetic result: %d\n", result);

    // Test memory operations
    int array[10];
    memory_ops(array, 10);
    printf("Memory ops result: %d\n", array[3]);

    // Test control flow
    control_flow(result);

    printf("Pipeline test complete.\n");
    return 0;
}
